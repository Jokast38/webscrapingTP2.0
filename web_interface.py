#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface web unifiée pour la recherche d'articles
"""

from flask import Flask, render_template, request, jsonify
from mongodb_manager import MongoDBManager
from datetime import datetime
import re

app = Flask(__name__)

# Initialiser MongoDB
try:
    db_manager = MongoDBManager()
    print("✅ Connexion MongoDB réussie")
except Exception as e:
    print(f"❌ Erreur MongoDB: {e}")
    db_manager = None

@app.route('/')
def index():
    """Page d'accueil"""
    try:
        if db_manager:
            # Récupérer toutes les données en une seule fois
            data = db_manager.get_data_for_interface()
            stats = data['stats']
            categories = data['categories']
            subcategories = data['subcategories']
            authors = data['authors']
            
            print(f"📊 Interface: {stats.get('total_articles', 0)} articles, "
                  f"{stats.get('categories_count', 0)} catégories, "
                  f"{stats.get('subcategories_count', 0)} sous-catégories, "
                  f"{stats.get('authors_count', 0)} auteurs")
        else:
            stats = {}
            categories = []
            subcategories = []
            authors = []
        
        return render_template('index.html', 
                             categories=categories,
                             subcategories=subcategories,
                             authors=authors,
                             stats=stats)
    except Exception as e:
        return f"Erreur: {e}"

@app.route('/search', methods=['POST'])
def search():
    """Recherche unifiée"""
    try:
        if not db_manager:
            return jsonify({'error': 'Base de données non disponible'})
        
        search_type = request.form.get('search_type', '')
        
        articles = []
        
        if search_type == 'category':
            category = request.form.get('category', '').strip()
            subcategory = request.form.get('category_subcategory', '').strip()
            
            if category and subcategory:
                # Recherche par catégorie ET sous-catégorie
                articles = db_manager.get_articles_by_category_and_subcategory(category, subcategory)
            elif category:
                # Recherche par catégorie seulement
                articles = db_manager.get_articles_by_category(category)
        
        elif search_type == 'subcategory':
            subcategory = request.form.get('subcategory', '').strip()
            if subcategory:
                articles = db_manager.get_articles_by_subcategory(subcategory)
        
        elif search_type == 'author':
            author = request.form.get('author', '').strip()
            if author:
                articles = db_manager.get_articles_by_author(author)
        
        elif search_type == 'date':
            start_date = request.form.get('start_date', '').strip()
            end_date = request.form.get('end_date', '').strip()
            if start_date and end_date:
                articles = db_manager.get_articles_by_date_range(start_date, end_date)
        
        elif search_type == 'title':
            title_search = request.form.get('title_search', '').strip()
            if title_search:
                articles = db_manager.search_in_title(title_search)
        
        else:
            return jsonify({'error': 'Type de recherche invalide'})
        
        # Format des résultats
        results = []
        for article in articles:
            # Conversion des ObjectId en string
            for field in ['_id', 'created_at', 'updated_at', 'scraped_at']:
                if field in article:
                    article[field] = str(article[field])
            
            results.append({
                'title': article.get('title', 'Sans titre'),
                'subcategory': article.get('subcategory', 'N/A'),
                'categories': article.get('categories', []),
                'subcategories': article.get('subcategories', []),
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

@app.route('/api/stats')
def api_stats():
    """API statistiques"""
    try:
        if not db_manager:
            return jsonify({'error': 'Base de données non disponible'})
        
        stats = db_manager.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/subcategories/<category>')
def get_subcategories_for_category(category):
    """API pour récupérer les sous-catégories d'une catégorie"""
    try:
        if not db_manager:
            return jsonify({
                'success': False,
                'error': 'Base de données non disponible'
            })
        
        print(f"🔍 API: Recherche sous-catégories pour: {category}")
        subcategories = db_manager.get_subcategories_by_category(category)
        
        print(f"✅ API: Trouvé {len(subcategories)} sous-catégories pour {category}")
        
        return jsonify({
            'success': True,
            'category': category,
            'subcategories': subcategories,
            'count': len(subcategories)
        })
    except Exception as e:
        print(f"❌ Erreur API subcategories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🌐 Interface web disponible sur: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)