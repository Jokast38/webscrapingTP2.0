#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour interroger la base de données MongoDB du Blog du Modérateur
"""

from mongodb_manager import MongoDBManager
import sys

def display_articles(articles, title="Articles trouvés"):
    """Affiche une liste d'articles de manière formatée"""
    print(f"\n{title}")
    print("=" * len(title))
    
    if not articles:
        print("Aucun article trouvé.")
        return
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.get('title', 'Sans titre')}")
        print(f"   Catégorie: {article.get('subcategory', 'N/A')}")
        print(f"   Auteur: {article.get('author', 'N/A')}")
        print(f"   Date: {article.get('date', 'N/A')}")
        print(f"   URL: {article.get('url', 'N/A')}")
        if article.get('summary'):
            print(f"   Résumé: {article['summary'][:100]}...")

def main():
    """Fonction principale avec menu interactif"""
    try:
        db_manager = MongoDBManager()
        
        while True:
            print("\n" + "="*60)
            print("RECHERCHE D'ARTICLES - BLOG DU MODÉRATEUR")
            print("="*60)
            print("1. Rechercher par catégorie")
            print("2. Rechercher par sous-catégorie") 
            print("3. Rechercher par auteur")
            print("4. Rechercher par plage de dates")
            print("5. Rechercher dans les titres")
            print("6. Afficher toutes les catégories")
            print("7. Afficher tous les auteurs")
            print("8. Afficher les statistiques")
            print("9. Quitter")
            
            choice = input("\nChoisissez une option (1-9): ").strip()
            
            if choice == '1':
                categories = db_manager.get_all_categories()
                if categories:
                    print(f"\nCatégories disponibles: {', '.join(categories)}")
                    category = input("Entrez le nom de la catégorie: ").strip()
                    articles = db_manager.get_articles_by_category(category)
                    display_articles(articles, f"Articles dans la catégorie '{category}'")
                else:
                    print("Aucune catégorie trouvée.")
            
            elif choice == '2':
                categories = db_manager.get_all_categories()
                if categories:
                    print(f"\nSous-catégories disponibles: {', '.join(categories)}")
                    subcategory = input("Entrez le nom de la sous-catégorie: ").strip()
                    articles = db_manager.get_articles_by_subcategory(subcategory)
                    display_articles(articles, f"Articles dans la sous-catégorie '{subcategory}'")
                else:
                    print("Aucune sous-catégorie trouvée.")
            
            elif choice == '3':
                authors = db_manager.get_all_authors()
                if authors:
                    print(f"\nAuteurs disponibles: {', '.join(authors)}")
                    author = input("Entrez le nom de l'auteur: ").strip()
                    articles = db_manager.get_articles_by_author(author)
                    display_articles(articles, f"Articles de l'auteur '{author}'")
                else:
                    print("Aucun auteur trouvé.")
            
            elif choice == '4':
                print("\nFormat de date: AAAA-MM-JJ (ex: 2025-07-15)")
                start_date = input("Date de début: ").strip()
                end_date = input("Date de fin: ").strip()
                
                try:
                    articles = db_manager.get_articles_by_date_range(start_date, end_date)
                    display_articles(articles, f"Articles entre {start_date} et {end_date}")
                except Exception as e:
                    print(f"Erreur de format de date: {e}")
            
            elif choice == '5':
                search_term = input("Entrez le terme à rechercher dans les titres: ").strip()
                articles = db_manager.search_in_title(search_term)
                display_articles(articles, f"Articles contenant '{search_term}' dans le titre")
            
            elif choice == '6':
                categories = db_manager.get_all_categories()
                print(f"\nCatégories disponibles ({len(categories)}):")
                for i, cat in enumerate(categories, 1):
                    print(f"{i}. {cat}")
            
            elif choice == '7':
                authors = db_manager.get_all_authors()
                print(f"\nAuteurs disponibles ({len(authors)}):")
                for i, author in enumerate(authors, 1):
                    print(f"{i}. {author}")
            
            elif choice == '8':
                db_manager.get_stats()
            
            elif choice == '9':
                print("Au revoir!")
                break
            
            else:
                print("Option invalide. Veuillez choisir entre 1 et 9.")
            
            input("\nAppuyez sur Entrée pour continuer...")
        
        db_manager.close()
        
    except Exception as e:
        print(f"Erreur: {e}")
        print("Assurez-vous que MongoDB est installé et en cours d'exécution.")

if __name__ == "__main__":
    main()
