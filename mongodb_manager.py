from pymongo import MongoClient
from datetime import datetime
import json
import re
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class MongoDBManager:
    def __init__(self, connection_string=None, database_name=None):
        """
        Initialise la connexion MongoDB (Atlas par défaut via .env)
        """
        if connection_string is None:
            # Récupération depuis les variables d'environnement
            connection_string = os.getenv('MONGODB_URI')
            if not connection_string:
                raise ValueError("MONGODB_URI non trouvé dans les variables d'environnement. Veuillez configurer le fichier .env")
        
        if database_name is None:
            database_name = os.getenv('MONGODB_DATABASE', 'wscrap')
        
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            collection_name = os.getenv('MONGODB_COLLECTION', 'articles')
            self.collection = self.db[collection_name]
            
            # Test de connexion
            self.client.admin.command('ping')
            print(f"✅ Connexion à MongoDB Atlas réussie - Base: {database_name}")
            
            # Créer les index pour optimiser les recherches
            self.create_indexes()
        except Exception as e:
            print(f"❌ Erreur de connexion à MongoDB: {e}")
            raise
    
    def create_indexes(self):
        """
        Crée les index pour optimiser les recherches
        """
        try:
            # Index sur l'URL pour éviter les doublons
            self.collection.create_index("url", unique=True)
            
            # Index sur les champs de recherche
            self.collection.create_index("subcategory")
            self.collection.create_index("author")
            self.collection.create_index("date")
            
            # Index texte pour la recherche full-text
            self.collection.create_index([
                ("title", "text"),
                ("summary", "text"),
                ("content", "text")
            ])
            
            print("📊 Index MongoDB créés pour optimiser les recherches")
        except Exception as e:
            print(f"⚠️ Erreur lors de la création des index: {e}")
            # Ne pas lever d'erreur, les index peuvent déjà exister
    
    def save_article(self, article_data):
        """
        Sauvegarde un article dans MongoDB avec gestion des doublons
        """
        try:
            # Vérifier que l'URL existe
            if not article_data.get('url'):
                print("⚠️ Article sans URL, ignoré")
                return None
                
            # Ajouter un timestamp de création
            article_data['created_at'] = datetime.now()
            article_data['updated_at'] = datetime.now()
            
            # Utiliser upsert pour gérer les doublons automatiquement
            result = self.collection.update_one(
                {'url': article_data.get('url')},  # Condition de recherche
                {'$set': article_data},            # Données à mettre à jour
                upsert=True                        # Insérer si pas trouvé
            )
            
            if result.upserted_id:
                print(f"✅ Nouvel article sauvegardé: {article_data.get('title', 'Sans titre')[:50]}...")
                return result.upserted_id
            else:
                print(f"🔄 Article mis à jour: {article_data.get('title', 'Sans titre')[:50]}...")
                return result.modified_count
                
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return None
    
    def save_articles(self, articles_list):
        """
        Sauvegarde une liste d'articles
        """
        saved_count = 0
        for article in articles_list:
            result = self.save_article(article)
            if result:
                saved_count += 1
        
        print(f"\nTotal: {saved_count}/{len(articles_list)} articles sauvegardés")
        return saved_count
    
    def get_articles_by_category(self, category):
        """
        Récupère tous les articles d'une catégorie donnée
        """
        try:
            # Recherche insensible à la casse
            query = {'subcategory': {'$regex': f'^{re.escape(category)}$', '$options': 'i'}}
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles dans la catégorie '{category}'")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par catégorie: {e}")
            return []
    
    def get_articles_by_subcategory(self, subcategory):
        """
        Récupère tous les articles d'une sous-catégorie donnée
        """
        try:
            # Recherche insensible à la casse
            query = {'subcategory': {'$regex': f'^{re.escape(subcategory)}$', '$options': 'i'}}
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles dans la sous-catégorie '{subcategory}'")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par sous-catégorie: {e}")
            return []
    
    def get_articles_by_author(self, author):
        """
        Récupère tous les articles d'un auteur donné
        """
        try:
            # Recherche insensible à la casse avec gestion des None
            query = {
                'author': {
                    '$regex': f'^{re.escape(author)}$', 
                    '$options': 'i'
                }
            }
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles de l'auteur '{author}'")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par auteur: {e}")
            return []
    
    def get_articles_by_date_range(self, start_date, end_date):
        """
        Récupère les articles dans une plage de dates (format AAAA-MM-JJ)
        """
        try:
            query = {
                'date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            articles = list(self.collection.find(query))
            print(f"Trouvé {len(articles)} articles entre {start_date} et {end_date}")
            return articles
        except Exception as e:
            print(f"Erreur lors de la recherche par date: {e}")
            return []
    
    def search_in_title(self, search_term):
        """
        Recherche dans les titres des articles
        """
        try:
            # Échapper les caractères spéciaux regex
            import re
            escaped_term = re.escape(search_term)
            
            query = {
                'title': {
                    '$regex': escaped_term,
                    '$options': 'i'  # Insensible à la casse
                }
            }
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles contenant '{search_term}' dans le titre")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche textuelle: {e}")
            return []
    
    def search_in_content(self, search_term):
        """
        Recherche dans le contenu des articles
        """
        try:
            import re
            escaped_term = re.escape(search_term)
            
            query = {
                '$or': [
                    {'title': {'$regex': escaped_term, '$options': 'i'}},
                    {'summary': {'$regex': escaped_term, '$options': 'i'}},
                    {'content': {'$regex': escaped_term, '$options': 'i'}}
                ]
            }
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles contenant '{search_term}' (titre, résumé ou contenu)")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche dans le contenu: {e}")
            return []
    
    def get_all_categories(self):
        """
        Récupère toutes les catégories disponibles
        """
        try:
            categories = self.collection.distinct('subcategory')
            return [cat for cat in categories if cat]  # Filtrer les None
        except Exception as e:
            print(f"Erreur lors de la récupération des catégories: {e}")
            return []
    
    def get_all_authors(self):
        """
        Récupère tous les auteurs disponibles
        """
        try:
            authors = self.collection.distinct('author')
            return [author for author in authors if author]  # Filtrer les None
        except Exception as e:
            print(f"Erreur lors de la récupération des auteurs: {e}")
            return []
    
    def get_stats(self):
        """
        Affiche des statistiques sur la collection
        """
        try:
            total_articles = self.collection.count_documents({})
            categories = self.get_all_categories()
            authors = self.get_all_authors()
            
            print(f"\n=== STATISTIQUES DE LA BASE ===")
            print(f"Total d'articles: {total_articles}")
            print(f"Nombre de catégories: {len(categories)}")
            print(f"Nombre d'auteurs: {len(authors)}")
            print(f"Catégories: {', '.join(categories[:10])}{'...' if len(categories) > 10 else ''}")
            
            return {
                'total_articles': total_articles,
                'categories_count': len(categories),
                'authors_count': len(authors),
                'categories': categories,
                'authors': authors
            }
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques: {e}")
            return {}
    
    def close(self):
        """
        Ferme la connexion MongoDB
        """
        if self.client:
            self.client.close()
            print("Connexion MongoDB fermée")
