#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rapide des fonctions de recherche MongoDB Atlas
"""

from mongodb_manager import MongoDBManager

def test_recherches():
    """Test les différentes fonctions de recherche"""
    try:
        print("🔗 Connexion à MongoDB Atlas...")
        db_manager = MongoDBManager()
        
        print("\n📊 Statistiques actuelles:")
        stats = db_manager.get_stats()
        
        print("\n🔍 Test de recherche par catégorie 'IA':")
        articles_ia = db_manager.get_articles_by_subcategory("IA")
        for i, article in enumerate(articles_ia[:3], 1):
            print(f"   {i}. {article['title']}")
            print(f"      Auteur: {article.get('author', 'N/A')}")
            print(f"      Date: {article.get('date', 'N/A')}")
        
        print("\n🔍 Test de recherche dans les titres 'Google':")
        articles_google = db_manager.search_in_title("Google")
        for i, article in enumerate(articles_google[:3], 1):
            print(f"   {i}. {article['title']}")
            print(f"      Catégorie: {article.get('subcategory', 'N/A')}")
        
        print("\n🔍 Test de recherche par auteur:")
        authors = db_manager.get_all_authors()
        if authors:
            first_author = authors[0]
            print(f"   Recherche pour l'auteur: {first_author}")
            articles_author = db_manager.get_articles_by_author(first_author)
            for i, article in enumerate(articles_author[:2], 1):
                print(f"   {i}. {article['title']}")
        
        print("\n✅ Tests de recherche terminés!")
        db_manager.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_recherches()
