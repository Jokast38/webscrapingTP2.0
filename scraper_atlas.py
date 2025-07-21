#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour MongoDB Atlas - Blog du Modérateur
Extrait 30 articles et les sauvegarde sur MongoDB Atlas
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from mongodb_manager import MongoDBManager
import time

def fetch_articles(url, max_articles=30):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"🌐 Récupération de la page principale: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles_data = []

        main_tag = soup.find('main')
        if not main_tag:
            print("❌ Aucune balise <main> trouvée.")
            return []

        articles = main_tag.find_all('article')[:max_articles]
        print(f"📰 {len(articles)} articles trouvés sur la page principale")
        
        for i, article in enumerate(articles, 1):
            print(f"\n📄 Traitement de l'article {i}/{len(articles)}...")
            
            img_div = article.find(
                'div',
                class_='post-thumbnail picture rounded-img'
            )
            img_tag = img_div.find('img') if img_div else None
            img_url = extract_img_url(img_tag)

            meta_div = article.find(
                'div',
                class_='entry-meta ms-md-5 pt-md-0 pt-3'
            )
            tag = (meta_div.find('span', class_='favtag color-b')
                       .get_text(strip=True)
                   ) if meta_div else None
            date = (meta_div.find('span', class_='posted-on t-def px-3')
                        .get_text(strip=True)
                   ) if meta_div else None
            formatted_date = format_date(date)

            header = (meta_div.find('header', class_='entry-header pt-1')
                      ) if meta_div else None
            a_tag = header.find('a') if header else None
            article_url = a_tag['href'] if a_tag and a_tag.has_attr('href') else None
            title = (a_tag.find('h3').get_text(strip=True)
                     ) if a_tag and a_tag.find('h3') else None

            summary_div = (meta_div.find('div', class_='entry-excerpt t-def t-size-def pt-1')
                           ) if meta_div else None
            summary = summary_div.get_text(strip=True) if summary_div else None

            # Récupérer les détails complets de l'article
            author = None
            content = None
            images = {}
            
            if article_url:
                print(f"   🔍 Récupération des détails: {title[:40]}...")
                author, content, images = fetch_article_details(article_url, headers)
                
                # Petite pause pour ne pas surcharger le serveur
                time.sleep(1)

            article_data = {
                'title': title,
                'thumbnail': img_url,
                'subcategory': tag,
                'summary': summary,
                'date': formatted_date,
                'original_date': date,
                'author': author,
                'content': content,
                'images': images,
                'url': article_url,
                'scraped_at': datetime.now()
            }
            
            articles_data.append(article_data)

        return articles_data

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
        return []

def fetch_article_details(article_url, headers):
    """Récupère les détails complets d'un article"""
    try:
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver l'article principal
        article = soup.find('article')
        if not article:
            return None, None, {}
            
        # Récupérer l'auteur avec plusieurs stratégies
        author = None
        author_selectors = [
            'span.author',
            'a.author', 
            'p.author',
            '.author-name',
            '.byline',
            '.entry-meta .author',
            'span[rel="author"]',
            '.post-author',
            '.article-author',
            '.entry-meta a[href*="/author/"]'
        ]
        
        for selector in author_selectors:
            author_elem = article.select_one(selector)
            if author_elem:
                author = author_elem.get_text(strip=True)
                if author:  # Vérifier que ce n'est pas vide
                    break
        
        # Si pas trouvé, chercher dans les métadonnées
        if not author:
            meta_author = soup.find('meta', attrs={'name': 'author'})
            if meta_author:
                author = meta_author.get('content', '').strip()
            
        # Récupérer le contenu principal
        content_div = article.find('div', class_='entry-content')
        if not content_div:
            content_div = article.find('div', class_='content')
        if not content_div:
            content_div = article.find('main')
            
        content_text = ""
        images_dict = {}
        img_counter = 1
        
        if content_div:
            # Nettoyer et récupérer le texte
            paragraphs = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content_parts = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20:  # Éviter les paragraphes vides ou trop courts
                    content_parts.append(text)
            
            content_text = "\n\n".join(content_parts)
            
            # Récupérer toutes les images dans l'article
            images = content_div.find_all('img')
            for img in images:
                img_url = extract_img_url(img)
                if img_url:
                    alt_text = img.get('alt', '')
                    title_text = img.get('title', '')
                    caption = alt_text or title_text or f"Image {img_counter}"
                    
                    images_dict[f"image_{img_counter}"] = {
                        'url': img_url,
                        'caption': caption
                    }
                    img_counter += 1
        
        return author, content_text, images_dict
        
    except Exception as e:
        print(f"   ⚠️ Erreur lors de la récupération de l'article: {e}")
        return None, None, {}

def format_date(date_str):
    """Convertit une date française en format AAAA-MM-JJ"""
    if not date_str:
        return None
    
    # Dictionnaire pour convertir les mois français
    mois_fr = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
    }
    
    try:
        # Pattern pour "16 juillet 2025"
        pattern = r'(\d{1,2})\s+(\w+)\s+(\d{4})'
        match = re.search(pattern, date_str.lower())
        
        if match:
            jour, mois, annee = match.groups()
            if mois in mois_fr:
                jour = jour.zfill(2)  # Ajoute un 0 si nécessaire
                return f"{annee}-{mois_fr[mois]}-{jour}"
    except Exception as e:
        print(f"⚠️ Erreur lors du formatage de la date '{date_str}': {e}")
    
    return date_str  # Retourne la date originale si conversion échoue

def extract_img_url(img_tag):
    if not img_tag:
        return None
    url_attributes = [
        'data-lazy-src',  
        'data-src',        
        'src'              
    ]
    for attr in url_attributes:
        if img_tag.has_attr(attr):
            url = img_tag[attr]
            if url and url.startswith('https://'):
                return url
    return None

if __name__ == "__main__":
    print("🚀 SCRAPER BLOG DU MODERATEUR - VERSION MONGODB ATLAS")
    print("=" * 60)
    
    # Configuration
    url = "https://www.blogdumoderateur.com/web/"
    max_articles = 30
    
    print(f"📊 Configuration:")
    print(f"   • URL: {url}")
    print(f"   • Nombre d'articles: {max_articles}")
    print(f"   • Base de données: MongoDB Atlas")
    
    # Connexion à MongoDB Atlas
    try:
        print(f"\n🔗 Connexion à MongoDB Atlas...")
        db_manager = MongoDBManager()
        
        # Récupération des articles
        print(f"\n📰 Récupération des articles...")
        articles = fetch_articles(url, max_articles)
        
        if articles:
            print(f"\n💾 Sauvegarde en MongoDB Atlas...")
            saved_count = db_manager.save_articles(articles)
            
            print(f"\n✅ TERMINÉ!")
            print(f"   • {len(articles)} articles récupérés")
            print(f"   • {saved_count} articles sauvegardés")
            
            # Afficher les statistiques
            print(f"\n📊 STATISTIQUES DE LA BASE:")
            stats = db_manager.get_stats()
            
        else:
            print("❌ Aucun article récupéré")
        
        db_manager.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("\nVérifiez:")
        print("• Votre connexion internet")
        print("• Les identifiants MongoDB Atlas")
        print("• L'installation de pymongo: pip install pymongo")
