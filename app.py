#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Front-end simple pour rechercher les articles du Blog du Modérateur
Utilise Flask pour créer une interface web
"""

from flask import Flask, render_template, request, jsonify
from mongodb_manager import MongoDBManager
import json
from datetime import datetime

app = Flask(__name__)

# Initialiser la connexion MongoDB
try:
    db_manager = MongoDBManager()
    print("Connexion MongoDB réussie pour le front-end")
except Exception as e:
    print(f"Erreur de connexion MongoDB: {e}")
    db_manager = None

@app.route('/')
def index():
    """Page d'accueil avec formulaire de recherche"""
    try:
        if db_manager:
            categories = db_manager.get_all_categories()
            authors = db_manager.get_all_authors()
            stats = db_manager.get_stats()
        else:
            categories = []
            authors = []
            stats = {}
            
        return render_template('index.html', 
                             categories=categories, 
                             authors=authors,
                             stats=stats)
    except Exception as e:
        return f"Erreur: {e}"

@app.route('/search', methods=['POST'])
def search():
    """Effectue la recherche selon les critères"""
    try:
        if not db_manager:
            return jsonify({'error': 'Base de données non disponible'})
        
        # Récupérer les paramètres de recherche
        search_type = request.form.get('search_type', '')
        search_value = request.form.get('search_value', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        category = request.form.get('category', '').strip()
        author = request.form.get('author', '').strip()
        title_search = request.form.get('title_search', '').strip()
        
        articles = []
        
        # Effectuer la recherche selon le type
        if search_type == 'category' and category:
            articles = db_manager.get_articles_by_subcategory(category)
        elif search_type == 'author' and author:
            articles = db_manager.get_articles_by_author(author)
        elif search_type == 'date' and start_date and end_date:
            articles = db_manager.get_articles_by_date_range(start_date, end_date)
        elif search_type == 'title' and title_search:
            articles = db_manager.search_in_title(title_search)
        else:
            return jsonify({'error': 'Paramètres de recherche invalides'})
        
        # Formater les résultats pour l'affichage
        results = []
        for article in articles:
            # Convertir ObjectId en string si nécessaire
            if '_id' in article:
                article['_id'] = str(article['_id'])
            if 'created_at' in article:
                article['created_at'] = str(article['created_at'])
            if 'updated_at' in article:
                article['updated_at'] = str(article['updated_at'])
                
            results.append({
                'title': article.get('title', 'Sans titre'),
                'subcategory': article.get('subcategory', 'N/A'),
                'author': article.get('author', 'N/A'),
                'date': article.get('date', 'N/A'),
                'summary': article.get('summary', 'Pas de résumé'),
                'url': article.get('url', '#'),
                'thumbnail': article.get('thumbnail', ''),
                'images_count': len(article.get('images', {}))
            })
        
        return jsonify({
            'success': True,
            'count': len(results),
            'articles': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/article/<path:article_url>')
def article_details(article_url):
    """Affiche les détails complets d'un article"""
    try:
        if not db_manager:
            return "Base de données non disponible"
        
        # Décoder l'URL
        import urllib.parse
        decoded_url = urllib.parse.unquote(article_url)
        
        # Chercher l'article dans la base
        article = db_manager.collection.find_one({'url': decoded_url})
        
        if not article:
            return "Article non trouvé"
        
        # Convertir ObjectId en string
        if '_id' in article:
            article['_id'] = str(article['_id'])
        
        return render_template('article.html', article=article)
        
    except Exception as e:
        return f"Erreur: {e}"

@app.route('/api/stats')
def api_stats():
    """API pour récupérer les statistiques"""
    try:
        if not db_manager:
            return jsonify({'error': 'Base de données non disponible'})
        
        stats = db_manager.get_stats()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("Démarrage du serveur Flask...")
    print("Interface disponible sur: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
