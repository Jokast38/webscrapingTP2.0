#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script avancé pour récupérer 30+ articles du Blog du Modérateur
Parcourt plusieurs pages et catégories
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from mongodb_manager import MongoDBManager
import time

def get_articles_from_multiple_pages(base_url, target_count=30):
    """
    Récupère des articles depuis plusieurs pages/catégories
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    all_articles = []
    
    # URLs à explorer
    urls_to_check = [
        "https://www.blogdumoderateur.com/web/",
        "https://www.blogdumoderateur.com/digital/",
        "https://www.blogdumoderateur.com/social-media/",
        "https://www.blogdumoderateur.com/tech/",
        "https://www.blogdumoderateur.com/marketing/",
        "https://www.blogdumoderateur.com/web/page/2/",  # Page 2
        "https://www.blogdumoderateur.com/digital/page/2/",  # Page 2
    ]
    
    for url in urls_to_check:
        if len(all_articles) >= target_count:
            break
            
        print(f"\n🌐 Exploration de: {url}")
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            main_tag = soup.find('main')
            if not main_tag:
                print("   ⚠️ Aucune balise <main> trouvée")
                continue
                
            articles = main_tag.find_all('article')
            print(f"   📰 {len(articles)} articles trouvés sur cette page")
            
            for article in articles:
                if len(all_articles) >= target_count:
                    break
                    
                article_data = extract_article_preview(article, headers)
                if article_data and article_data['url']:
                    # Vérifier si on a déjà cet article
                    if not any(a['url'] == article_data['url'] for a in all_articles):
                        all_articles.append(article_data)
                        print(f"   ✅ Article ajouté: {article_data['title'][:50]}...")
            
            # Pause entre les pages
            time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ Erreur pour {url}: {e}")
            continue
    
    print(f"\n📊 Total collecté: {len(all_articles)} articles uniques")
    return all_articles

def extract_article_preview(article, headers):
    """
    Extrait les données de prévisualisation d'un article
    """
    try:
        # Image
        img_div = article.find('div', class_='post-thumbnail picture rounded-img')
        img_tag = img_div.find('img') if img_div else None
        img_url = extract_img_url(img_tag)

        # Métadonnées
        meta_div = article.find('div', class_='entry-meta ms-md-5 pt-md-0 pt-3')
        if not meta_div:
            meta_div = article.find('div', class_='entry-meta')
        
        tag = None
        date = None
        if meta_div:
            tag_elem = meta_div.find('span', class_='favtag color-b')
            if not tag_elem:
                tag_elem = meta_div.find('span', class_='favtag')
            tag = tag_elem.get_text(strip=True) if tag_elem else None
            
            date_elem = meta_div.find('span', class_='posted-on t-def px-3')
            if not date_elem:
                date_elem = meta_div.find('span', class_='posted-on')
            date = date_elem.get_text(strip=True) if date_elem else None

        formatted_date = format_date(date)

        # Titre et URL
        header = meta_div.find('header', class_='entry-header pt-1') if meta_div else None
        if not header:
            header = article.find('header')
        
        a_tag = header.find('a') if header else None
        article_url = a_tag['href'] if a_tag and a_tag.has_attr('href') else None
        
        title_elem = a_tag.find('h3') if a_tag else None
        if not title_elem:
            title_elem = a_tag.find('h2') if a_tag else None
        if not title_elem:
            title_elem = a_tag.find('h1') if a_tag else None
        title = title_elem.get_text(strip=True) if title_elem else None

        # Résumé
        summary_div = meta_div.find('div', class_='entry-excerpt t-def t-size-def pt-1') if meta_div else None
        if not summary_div:
            summary_div = meta_div.find('div', class_='entry-excerpt') if meta_div else None
        summary = summary_div.get_text(strip=True) if summary_div else None

        if not article_url or not title:
            return None

        # Récupérer les détails complets
        print(f"      🔍 Détails de: {title[:40]}...")
        author, content, images = fetch_article_details(article_url, headers)
        
        # Pause pour ne pas surcharger
        time.sleep(1)

        return {
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
    
    except Exception as e:
        print(f"      ⚠️ Erreur extraction article: {e}")
        return None

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
            
        # Récupérer l'auteur
        author = None
        author_selectors = [
            'span.author',
            'a.author', 
            '.author-name',
            '.byline',
            '.entry-meta .author',
            'span[rel="author"]',
            '.post-author',
            '.article-author',
            '.entry-meta a[href*="/author/"]',
            '.entry-meta span:contains("Par")'
        ]
        
        for selector in author_selectors:
            try:
                author_elem = article.select_one(selector)
                if author_elem:
                    author_text = author_elem.get_text(strip=True)
                    # Nettoyer le texte de l'auteur
                    author_text = re.sub(r'^Par\s+', '', author_text, flags=re.IGNORECASE)
                    if author_text and len(author_text) > 2:
                        author = author_text
                        break
            except:
                continue
        
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
                if text and len(text) > 20:
                    content_parts.append(text)
            
            content_text = "\n\n".join(content_parts)
            
            # Récupérer les images
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
        return None, None, {}

def format_date(date_str):
    """Convertit une date française en format AAAA-MM-JJ"""
    if not date_str:
        return None
    
    mois_fr = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
    }
    
    try:
        pattern = r'(\d{1,2})\s+(\w+)\s+(\d{4})'
        match = re.search(pattern, date_str.lower())
        
        if match:
            jour, mois, annee = match.groups()
            if mois in mois_fr:
                jour = jour.zfill(2)
                return f"{annee}-{mois_fr[mois]}-{jour}"
    except Exception as e:
        pass
    
    return date_str

def extract_img_url(img_tag):
    if not img_tag:
        return None
    url_attributes = ['data-lazy-src', 'data-src', 'src']
    for attr in url_attributes:
        if img_tag.has_attr(attr):
            url = img_tag[attr]
            if url and url.startswith('https://'):
                return url
    return None

if __name__ == "__main__":
    print("🚀 SCRAPER AVANCÉ - BLOG DU MODÉRATEUR")
    print("=" * 60)
    
    target_count = 30
    print(f"🎯 Objectif: {target_count} articles")
    
    try:
        # Connexion à MongoDB Atlas
        print(f"\n🔗 Connexion à MongoDB Atlas...")
        db_manager = MongoDBManager()
        
        # Récupération des articles
        print(f"\n📰 Récupération des articles depuis plusieurs pages...")
        articles = get_articles_from_multiple_pages("https://www.blogdumoderateur.com", target_count)
        
        if articles:
            print(f"\n💾 Sauvegarde de {len(articles)} articles en MongoDB Atlas...")
            saved_count = db_manager.save_articles(articles)
            
            print(f"\n✅ TERMINÉ!")
            print(f"   • {len(articles)} articles récupérés")
            print(f"   • {saved_count} articles sauvegardés")
            
            # Statistiques finales
            print(f"\n📊 STATISTIQUES FINALES:")
            stats = db_manager.get_stats()
            
        else:
            print("❌ Aucun article récupéré")
        
        db_manager.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
