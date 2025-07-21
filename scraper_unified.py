#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script unifié de scraping - Blog du Modérateur
Remplace tous les autres scrapers avec options flexibles
"""

import argparse
import sys
from core_scraper import BlogScraperCore
from mongodb_manager import MongoDBManager

def main():
    parser = argparse.ArgumentParser(description='Scraper unifié Blog du Modérateur')
    parser.add_argument('--mode', choices=['mongo', 'multi'], default='mongo',
                       help='Mode de fonctionnement (default: mongo)')
    parser.add_argument('--count', type=int, default=30,
                       help='Nombre d\'articles à récupérer (default: 30)')
    parser.add_argument('--output', default='articles.json',
                       help='Fichier de sortie JSON (default: articles.json)')
    parser.add_argument('--url', default='https://www.blogdumoderateur.com/web/',
                       help='URL de base (default: web section)')
    
    args = parser.parse_args()
    
    print("🚀 SCRAPER UNIFIÉ - BLOG DU MODÉRATEUR")
    print("=" * 60)
    print(f"📊 Mode: {args.mode}")
    print(f"📰 Articles: {args.count}")
    
    # Initialisation du scraper
    scraper = BlogScraperCore()
    
    try:
        if args.mode == 'multi':
            # Mode multi-pages avec sauvegarde JSON
            print(f"\n📥 Mode multi-pages - récupération depuis plusieurs sources")
            urls = [
                "https://www.blogdumoderateur.com/web/",
                "https://www.blogdumoderateur.com/digital/",
                "https://www.blogdumoderateur.com/social-media/",
                "https://www.blogdumoderateur.com/tech/",
                "https://www.blogdumoderateur.com/marketing/",
                "https://www.blogdumoderateur.com/web/page/2/",
                "https://www.blogdumoderateur.com/digital/page/2/",
            ]
            
            articles = scraper.fetch_articles_multi_pages(urls, args.count)
            
            if articles:
                scraper.save_to_json(articles, args.output)
                scraper.display_summary(articles)
            else:
                print("❌ Aucun article récupéré")
        
        elif args.mode == 'mongo':
            # Mode MongoDB - récupération et sauvegarde en base
            print(f"\n📥 Mode MongoDB - récupération et sauvegarde en base")
            
            # Connexion MongoDB
            print("🔗 Connexion à MongoDB...")
            db_manager = MongoDBManager()
            
            # Récupération multi-pages par défaut pour MongoDB
            urls = [
                "https://www.blogdumoderateur.com/web/",
                "https://www.blogdumoderateur.com/digital/",
                "https://www.blogdumoderateur.com/social-media/",
                "https://www.blogdumoderateur.com/tech/",
                "https://www.blogdumoderateur.com/marketing/",
            ]
            
            articles = scraper.fetch_articles_multi_pages(urls, args.count)
            
            if articles:
                print(f"\n💾 Sauvegarde de {len(articles)} articles en MongoDB...")
                saved_count = db_manager.save_articles(articles)
                
                print(f"\n✅ TERMINÉ!")
                print(f"   • {len(articles)} articles récupérés")
                print(f"   • {saved_count} articles sauvegardés")
                
                # Statistiques finales
                print(f"\n📊 STATISTIQUES DE LA BASE:")
                db_manager.get_stats()
            else:
                print("❌ Aucun article récupéré")
            
            db_manager.close()
        
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt demandé par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()