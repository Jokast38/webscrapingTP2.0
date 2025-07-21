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
    
    def get_all_categories(self):
        """
        Récupère toutes les catégories principales uniques depuis le champ categories (array)
        Ces catégories viennent du span.cat[data-cat] de la classe cats-list
        """
        try:
            # Récupérer les catégories depuis le champ categories (array)
            categories = self.collection.distinct('categories')
            categories = [cat for cat in categories if cat and cat.strip()]
            categories.sort()
            
            print(f"📊 Catégories trouvées: {len(categories)}")
            if categories:
                print(f"🏷️ Catégories: {', '.join(categories)}")
            
            return categories
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des catégories: {e}")
            # Retourner les catégories par défaut en cas d'erreur
            return ['Web', 'Marketing', 'Social', 'Tech']

    def get_all_subcategories(self):
        """
        Récupère toutes les sous-catégories uniques depuis le champ subcategories (array)
        Ces sous-catégories viennent des <li> de la classe tags-list
        """
        try:
            # Pipeline d'agrégation pour récupérer les subcategories (depuis les <li> de tags-list)
            pipeline = [
                {'$unwind': '$subcategories'},
                {'$group': {'_id': '$subcategories'}},
                {'$sort': {'_id': 1}}
            ]
            subcategories_from_array = [doc['_id'] for doc in self.collection.aggregate(pipeline)]
            
            # Ajouter aussi les subcategory (tag principal de la page d'accueil)
            main_subcategories = self.collection.distinct('subcategory')
            main_subcategories = [cat for cat in main_subcategories if cat and cat.strip()]
            
            # Combiner et dédupliquer
            all_subcategories = list(set(subcategories_from_array + main_subcategories))
            all_subcategories = [sub for sub in all_subcategories if sub and sub.strip()]
            all_subcategories.sort()
            
            print(f"📊 Sous-catégories trouvées: {len(all_subcategories)}")
            if all_subcategories:
                print(f"🔖 Exemples: {', '.join(all_subcategories[:5])}{'...' if len(all_subcategories) > 5 else ''}")
            
            return all_subcategories
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des sous-catégories: {e}")
            return []
    
    def get_articles_by_category(self, category):
        """
        Récupère tous les articles d'une catégorie principale donnée
        Recherche dans le champ categories (array) - une seule catégorie par article
        """
        try:
            import re
            # Recherche exacte dans le tableau des catégories (qui ne contient qu'un élément)
            query = {'categories': {'$regex': f'^{re.escape(category)}$', '$options': 'i'}}
            
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles dans la catégorie '{category}'")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par catégorie: {e}")
            return []

    def get_articles_by_category_and_subcategory(self, category, subcategory):
        """
        Récupère les articles d'une catégorie ET d'une sous-catégorie spécifiques
        """
        try:
            import re
            
            # Construire la requête avec catégorie ET sous-catégorie
            query = {
                '$and': [
                    {'categories': {'$regex': f'^{re.escape(category)}$', '$options': 'i'}},
                    {'$or': [
                        {'subcategories': {'$regex': f'^{re.escape(subcategory)}$', '$options': 'i'}},
                        {'subcategory': {'$regex': f'^{re.escape(subcategory)}$', '$options': 'i'}}
                    ]}
                ]
            }
            
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles pour '{category}' > '{subcategory}'")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par catégorie + sous-catégorie: {e}")
            return []

    def get_subcategories_by_category(self, category):
        """
        Récupère les sous-catégories associées à une catégorie principale
        Utilise maintenant les vraies catégories de la base
        """
        try:
            import re
            
            # Recherche des articles de cette catégorie
            query = {'categories': {'$regex': f'^{re.escape(category)}$', '$options': 'i'}}
            
            print(f"🔍 Recherche sous-catégories pour '{category}' avec requête: {query}")
            
            # Pipeline d'agrégation pour récupérer les subcategories uniques
            pipeline = [
                {'$match': query},
                {'$unwind': '$subcategories'},
                {'$group': {'_id': '$subcategories'}},
                {'$sort': {'_id': 1}}
            ]
            
            subcategories_from_array = [doc['_id'] for doc in self.collection.aggregate(pipeline)]
            print(f"📦 Sous-catégories depuis array: {len(subcategories_from_array)}")
            
            # Récupérer aussi les subcategory (tags principaux) pour cette catégorie
            articles = list(self.collection.find(query, {'subcategory': 1}))
            main_subcategories = list(set([article.get('subcategory') for article in articles if article.get('subcategory')]))
            print(f"🎯 Tags principaux: {len(main_subcategories)}")
            
            # Combiner et dédupliquer
            all_subcategories = list(set(subcategories_from_array + main_subcategories))
            all_subcategories = [sub for sub in all_subcategories if sub and sub.strip()]
            all_subcategories.sort()
            
            print(f"✅ Sous-catégories finales pour '{category}': {len(all_subcategories)}")
            if all_subcategories:
                print(f"📋 Exemples: {', '.join(all_subcategories[:5])}{'...' if len(all_subcategories) > 5 else ''}")
            
            return all_subcategories
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des sous-catégories pour '{category}': {e}")
            return []
    
    def get_all_authors(self):
        """
        Récupère tous les auteurs uniques
        """
        try:
            authors = self.collection.distinct('author')
            # Filtrer les valeurs None et vides
            authors = [author for author in authors if author and author.strip()]
            authors.sort()
            
            print(f"📊 Auteurs trouvés: {len(authors)}")
            if authors:
                print(f"✍️ Exemples: {', '.join(authors[:5])}{'...' if len(authors) > 5 else ''}")
            
            return authors
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des auteurs: {e}")
            return []
    
    def get_stats(self):
        """
        Récupère les statistiques pour l'interface web (optimisé)
        """
        try:
            total_articles = self.collection.count_documents({})
            
            # Catégories principales fixes
            categories = self.get_all_categories()
            categories_count = len(categories)
            
            # Sous-catégories depuis la base
            subcategories_count = len(self.get_all_subcategories())
            
            # Auteurs
            authors_count = len(self.get_all_authors())
            
            print(f"\n=== STATISTIQUES DE LA BASE ===")
            print(f"📰 Total d'articles: {total_articles}")
            print(f"🏷️ Nombre de catégories: {categories_count}")
            print(f"🔖 Nombre de sous-catégories: {subcategories_count}")
            print(f"✍️ Nombre d'auteurs: {authors_count}")
            
            return {
                'total_articles': total_articles,
                'categories_count': categories_count,
                'subcategories_count': subcategories_count,
                'authors_count': authors_count
            }
        except Exception as e:
            print(f"❌ Erreur lors du calcul des statistiques: {e}")
            return {
                'total_articles': 0,
                'categories_count': 4,
                'subcategories_count': 0,
                'authors_count': 0
            }
    
    def get_data_for_interface(self):
        """
        Récupère toutes les données nécessaires pour l'interface web
        """
        try:
            stats = self.get_stats()
            categories = self.get_all_categories()
            subcategories = self.get_all_subcategories()
            authors = self.get_all_authors()
            
            return {
                'stats': stats,
                'categories': categories,
                'subcategories': subcategories,
                'authors': authors
            }
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des données: {e}")
            return {
                'stats': {
                    'total_articles': 0,
                    'categories_count': 4,
                    'subcategories_count': 0,
                    'authors_count': 0
                },
                'categories': ['Web', 'Marketing', 'Social', 'Tech'],
                'subcategories': [],
                'authors': []
            }
    
    def close(self):
        """
        Ferme la connexion MongoDB
        """
        if self.client:
            self.client.close()
            print("Connexion MongoDB fermée")
    
    def get_articles_by_subcategory(self, subcategory):
        """
        Récupère tous les articles d'une sous-catégorie donnée
        """
        try:
            import re
            query = {
                '$or': [
                    {'subcategories': {'$regex': f'^{re.escape(subcategory)}$', '$options': 'i'}},
                    {'subcategory': {'$regex': f'^{re.escape(subcategory)}$', '$options': 'i'}}
                ]
            }
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles avec la sous-catégorie '{subcategory}'")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par sous-catégorie: {e}")
            return []

    def get_articles_by_author(self, author):
        """
        Récupère tous les articles d'un auteur donné
        """
        try:
            import re
            query = {'author': {'$regex': f'^{re.escape(author)}$', '$options': 'i'}}
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles de l'auteur '{author}'")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par auteur: {e}")
            return []

    def get_articles_by_date_range(self, start_date, end_date):
        """
        Récupère les articles dans une plage de dates
        """
        try:
            from datetime import datetime
            
            # Convertir les chaînes de date en format MongoDB
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Requête sur le champ created_at
            query = {
                'created_at': {
                    '$gte': start,
                    '$lte': end
                }
            }
            
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles entre {start_date} et {end_date}")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par date: {e}")
            return []

    def search_in_title(self, search_term):
        """
        Recherche dans les titres des articles
        """
        try:
            import re
            query = {'title': {'$regex': re.escape(search_term), '$options': 'i'}}
            articles = list(self.collection.find(query))
            print(f"🔍 Trouvé {len(articles)} articles avec '{search_term}' dans le titre")
            return articles
        except Exception as e:
            print(f"❌ Erreur lors de la recherche dans les titres: {e}")
            return []
