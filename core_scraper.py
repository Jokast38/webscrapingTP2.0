#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module principal de scraping - Blog du Modérateur
Respecte le principe DRY et évite toutes les répétitions
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import json
from typing import List, Dict, Optional, Tuple

class BlogScraperCore:
    """Classe principale pour le scraping du Blog du Modérateur"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.mois_fr = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }
        
    def extract_img_url(self, img_tag) -> Optional[str]:
        """Extrait l'URL d'une image depuis différents attributs"""
        if not img_tag:
            return None
        
        url_attributes = ['data-lazy-src', 'data-src', 'src']
        for attr in url_attributes:
            if img_tag.has_attr(attr):
                url = img_tag[attr]
                if url and url.startswith('https://'):
                    return url
        return None

    def format_date(self, date_str: str) -> Optional[str]:
        """Convertit une date française en format AAAA-MM-JJ"""
        if not date_str:
            return None
        
        try:
            pattern = r'(\d{1,2})\s+(\w+)\s+(\d{4})'
            match = re.search(pattern, date_str.lower())
            
            if match:
                jour, mois, annee = match.groups()
                if mois in self.mois_fr:
                    jour = jour.zfill(2)
                    return f"{annee}-{self.mois_fr[mois]}-{jour}"
        except Exception as e:
            print(f"⚠️ Erreur formatage date '{date_str}': {e}")
        
        return date_str

    def extract_date_from_article(self, article) -> Tuple[Optional[str], Optional[str]]:
        """Extrait la date d'un article (date lisible, date formatée)"""
        # Méthode principale : time.entry-date
        date_elem = article.find('time', class_='entry-date published updated')
        if date_elem:
            datetime_attr = date_elem.get('datetime')
            if datetime_attr:
                try:
                    parsed_date = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                    formatted_date = parsed_date.strftime('%Y-%m-%d')
                    date = date_elem.get_text(strip=True)
                    return date, formatted_date
                except:
                    pass
            
            # Fallback sur le texte
            date = date_elem.get_text(strip=True)
            return date, self.format_date(date)
        
        # Fallback sur l'ancienne méthode
        meta_div = article.find('div', class_='entry-meta')
        if meta_div:
            date_elem = meta_div.find('span', class_='posted-on')
            if date_elem:
                date = date_elem.get_text(strip=True)
                return date, self.format_date(date)
        
        return None, None

    def extract_images_with_captions(self, content_div) -> Dict[str, Dict[str, str]]:
        """Extrait les images avec leurs légendes"""
        images_dict = {}
        img_counter = 1
        
        # Méthode 1: Figures avec figcaption
        figures = content_div.find_all('figure')
        for figure in figures:
            img = figure.find('img')
            if img:
                img_url = self.extract_img_url(img)
                if img_url:
                    figcaption = figure.find('figcaption')
                    caption = (figcaption.get_text(strip=True) if figcaption 
                             else img.get('alt', '') or img.get('title', '') or f"Image {img_counter}")
                    
                    images_dict[f"image_{img_counter}"] = {
                        'url': img_url,
                        'caption': caption
                    }
                    img_counter += 1
        
        # Méthode 2: Divs avec caption
        caption_divs = content_div.find_all('div', class_=re.compile(r'(caption|wp-caption)'))
        for div in caption_divs:
            img = div.find('img')
            if img:
                img_url = self.extract_img_url(img)
                if img_url:
                    caption_text = div.find(class_=re.compile(r'(caption-text|wp-caption-text)'))
                    caption = (caption_text.get_text(strip=True) if caption_text 
                             else re.sub(r'\s+', ' ', div.get_text(strip=True))
                             or img.get('alt', '') or img.get('title', '') or f"Image {img_counter}")
                    
                    img_key = f"image_{img_counter}"
                    if img_key not in images_dict:
                        images_dict[img_key] = {
                            'url': img_url,
                            'caption': caption
                        }
                        img_counter += 1
        
        # Méthode 3: Images isolées
        images = content_div.find_all('img')
        for img in images:
            img_url = self.extract_img_url(img)
            if img_url and not any(existing['url'] == img_url for existing in images_dict.values()):
                caption = img.get('alt', '') or img.get('title', '') or f"Image {img_counter}"
                images_dict[f"image_{img_counter}"] = {
                    'url': img_url,
                    'caption': caption
                }
                img_counter += 1
        
        return images_dict

    def extract_categories_and_subcategories(self, article) -> Tuple[List[str], List[str]]:
        """
        Extrait les catégories et sous-catégories depuis les éléments HTML appropriés
        - Catégorie : depuis cats-list > span.cat[data-cat] (une seule par article)
        - Sous-catégories : depuis tags-list avec les li
        """
        categories = []
        subcategories = []
        
        try:
            # Catégorie principale (span.cat avec data-cat dans cats-list)
            cats_div = article.find("div", class_="cats-list")
            if cats_div:
                cat_span = cats_div.find("span", class_="cat")
                if cat_span and cat_span.has_attr("data-cat"):
                    categorie = cat_span["data-cat"]
                    if categorie and categorie.strip():
                        categories.append(categorie.strip())
            
            # Sous-catégories (li enfants de tags-list)
            tags_lists = article.find_all(class_='tags-list')
            for tags_list in tags_lists:
                li_elements = tags_list.find_all('li')
                for li in li_elements:
                    link = li.find('a')
                    if link:
                        subcategory_name = link.get_text(strip=True)
                        if subcategory_name and subcategory_name not in subcategories:
                            subcategories.append(subcategory_name)
            
            print(f"📊 Extracté {len(categories)} catégorie(s) et {len(subcategories)} sous-catégories")
            if categories:
                print(f"🏷️ Catégorie: {categories[0]}")
            if subcategories:
                print(f"🔖 Sous-catégories: {', '.join(subcategories[:3])}{'...' if len(subcategories) > 3 else ''}")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des catégories: {e}")
        
        return categories, subcategories

    def fetch_article_details(self, article_url: str) -> Tuple[Optional[str], Optional[str], Dict, List[str], List[str]]:
        """Récupère les détails complets d'un article"""
        try:
            print(f"       🌐 Accès à: {article_url}")
            response = requests.get(article_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            article = soup.find('article')
            if not article:
                print(f"       ❌ Pas d'article trouvé sur la page")
                return None, None, {}, [], []
            
            # Auteur
            author = None
            byline_elem = article.find(class_='byline')
            if byline_elem:
                author = byline_elem.get_text(strip=True)
            else:
                meta_author = soup.find('meta', attrs={'name': 'author'})
                if meta_author:
                    author = meta_author.get('content', '').strip()
            
            # ✅ CORRECTION : passer soup au lieu de article
            print(f"       🔍 Recherche catégories dans la page détaillée...")
            categories, subcategories = self.extract_categories_and_subcategories(soup)  # ← soup !
            
            print(f"       📊 Trouvé: {len(categories)} catégorie(s), {len(subcategories)} sous-catégorie(s)")
            
            # Contenu principal
            content_div = (article.find('div', class_='entry-content') or 
                          article.find('div', class_='content') or 
                          article.find('main'))
            
            content_text = ""
            images_dict = {}
            
            if content_div:
                # Texte
                paragraphs = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                content_parts = [p.get_text(strip=True) for p in paragraphs 
                               if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20]
                content_text = "\n\n".join(content_parts)
                
                # Images
                images_dict = self.extract_images_with_captions(content_div)
        
            return author, content_text, images_dict, categories, subcategories
        
        except Exception as e:
            print(f"⚠️ Erreur article {article_url}: {e}")
            return None, None, {}, [], []

    def extract_article_preview(self, article) -> Optional[Dict]:
        """Extrait les données de prévisualisation d'un article"""
        try:
            # Image
            img_div = article.find('div', class_='post-thumbnail picture rounded-img')
            img_tag = img_div.find('img') if img_div else None
            img_url = self.extract_img_url(img_tag)

            # Métadonnées
            meta_div = (article.find('div', class_='entry-meta ms-md-5 pt-md-0 pt-3') or
                       article.find('div', class_='entry-meta'))
            
            # Tag principal
            tag = None
            if meta_div:
                tag_elem = (meta_div.find('span', class_='favtag color-b') or
                           meta_div.find('span', class_='favtag'))
                tag = tag_elem.get_text(strip=True) if tag_elem else None
            
            # Date
            date, formatted_date = self.extract_date_from_article(article)

            # Titre et URL
            header = (meta_div.find('header', class_='entry-header pt-1') if meta_div 
                     else article.find('header'))
            a_tag = header.find('a') if header else None
            article_url = a_tag.get('href') if a_tag and a_tag.has_attr('href') else None
            
            title = None
            if a_tag:
                title_elem = (a_tag.find('h3') or a_tag.find('h2') or a_tag.find('h1'))
                title = title_elem.get_text(strip=True) if title_elem else None

            # Résumé
            summary = None
            if meta_div:
                summary_div = (meta_div.find('div', class_='entry-excerpt t-def t-size-def pt-1') or
                              meta_div.find('div', class_='entry-excerpt'))
                summary = summary_div.get_text(strip=True) if summary_div else None

            if not article_url or not title:
                return None

            return {
                'title': title,
                'thumbnail': img_url,
                'subcategory': tag,
                'summary': summary,
                'date': formatted_date,
                'original_date': date,
                'url': article_url
            }
        
        except Exception as e:
            print(f"⚠️ Erreur extraction preview: {e}")
            return None

    def fetch_articles_from_url(self, url: str, max_articles: int = 30) -> List[Dict]:
        """Récupère les articles depuis une URL donnée"""
        try:
            print(f"🌐 Récupération: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            main_tag = soup.find('main')
            if not main_tag:
                print(f"⚠️ Aucune balise <main> trouvée sur {url}")
                return []

            articles = main_tag.find_all('article')[:max_articles]
            print(f"📰 {len(articles)} articles trouvés")
            
            articles_data = []
            
            for i, article in enumerate(articles, 1):
                print(f"📄 Article {i}/{len(articles)}: ", end="")
                
                # Extraction preview
                preview_data = self.extract_article_preview(article)
                if not preview_data:
                    print("❌ Ignoré")
                    continue
                
                print(f"{preview_data['title'][:40]}...")
                
                # Détails complets
                print(f"   🔍 Récupération détails...")
                author, content, images, categories, subcategories = self.fetch_article_details(preview_data['url'])
                
                # Assemblage final
                article_data = {
                    **preview_data,
                    'author': author,
                    'content': content,
                    'images': images,
                    'categories': categories,
                    'subcategories': subcategories,
                    'scraped_at': datetime.now()
                }
                
                articles_data.append(article_data)
                
                # Pause pour ne pas surcharger
                time.sleep(1)
            
            return articles_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur requête {url}: {e}")
            return []

    def fetch_articles_multi_pages(self, base_urls: List[str], target_count: int = 30) -> List[Dict]:
        """Récupère des articles depuis plusieurs pages/catégories"""
        all_articles = []
        seen_urls = set()
        
        for url in base_urls:
            if len(all_articles) >= target_count:
                break
            
            articles = self.fetch_articles_from_url(url, target_count - len(all_articles))
            
            # Éviter les doublons
            for article in articles:
                if article['url'] not in seen_urls:
                    all_articles.append(article)
                    seen_urls.add(article['url'])
                    
                if len(all_articles) >= target_count:
                    break
            
            # Pause entre les pages
            time.sleep(2)
        
        print(f"\n📊 Total collecté: {len(all_articles)} articles uniques")
        return all_articles

    def save_to_json(self, articles: List[Dict], filename: str = "articles.json") -> bool:
        """Sauvegarde les articles en JSON"""
        try:
            # Sérialisation des datetime
            articles_serializable = []
            for article in articles:
                article_copy = article.copy()
                if isinstance(article_copy.get('scraped_at'), datetime):
                    article_copy['scraped_at'] = article_copy['scraped_at'].isoformat()
                articles_serializable.append(article_copy)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles_serializable, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Articles sauvegardés dans {filename}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde JSON: {e}")
            return False

    def display_summary(self, articles: List[Dict]) -> None:
        """Affiche un résumé des articles récupérés"""
        print(f"\n{'='*80}")
        print(f"🎉 RÉSUMÉ DU SCRAPING")
        print(f"{'='*80}")
        print(f"📰 Total d'articles: {len(articles)}")
        
        # Statistiques
        all_categories = set()
        all_subcategories = set()
        authors = set()
        
        for article in articles:
            if article.get('categories'):
                all_categories.update(article['categories'])
            if article.get('subcategories'):
                all_subcategories.update(article['subcategories'])
            if article.get('author'):
                authors.add(article['author'])
        
        print(f"🏷️ Catégories uniques: {len(all_categories)}")
        print(f"🔖 Sous-catégories uniques: {len(all_subcategories)}")
        print(f"✍️ Auteurs uniques: {len(authors)}")
        
        if all_categories:
            categories_sample = ', '.join(list(all_categories)[:5])
            print(f"📋 Catégories: {categories_sample}{'...' if len(all_categories) > 5 else ''}")
        
        if all_subcategories:
            subcategories_sample = ', '.join(list(all_subcategories)[:5])
            print(f"🔖 Sous-catégories: {subcategories_sample}{'...' if len(all_subcategories) > 5 else ''}")
        
        # Aperçu des premiers articles
        print(f"\n📋 APERÇU DES PREMIERS ARTICLES:")
        for i, article in enumerate(articles[:3], 1):
            print(f"\n📄 ARTICLE {i}: {article.get('title', 'Sans titre')}")
            print(f"   🏷️ Tag: {article.get('subcategory', 'N/A')}")
            print(f"   📂 Catégories: {', '.join(article.get('categories', []))}")
            print(f"   🔖 Sous-catégories: {', '.join(article.get('subcategories', []))}")
            print(f"   ✍️ Auteur: {article.get('author', 'N/A')}")
            print(f"   📅 Date: {article.get('date', 'N/A')}")
            print(f"   🖼️ Images: {len(article.get('images', {}))}")