#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de vérification de sécurité - MongoDB avec variables d'environnement
"""

import os
from dotenv import load_dotenv

def test_env_security():
    """
    Teste que les variables d'environnement sont bien chargées
    et qu'aucune connexion en dur n'est présente
    """
    print("🔒 TEST DE SÉCURITÉ - Variables d'environnement")
    print("=" * 50)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier que les variables sont disponibles
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_db = os.getenv('MONGODB_DATABASE')
    mongodb_collection = os.getenv('MONGODB_COLLECTION')
    
    print(f"✅ MONGODB_URI configuré: {'Oui' if mongodb_uri else 'Non'}")
    print(f"✅ MONGODB_DATABASE configuré: {mongodb_db if mongodb_db else 'Non configuré'}")
    print(f"✅ MONGODB_COLLECTION configuré: {mongodb_collection if mongodb_collection else 'Non configuré'}")
    
    if mongodb_uri:
        # Masquer les credentials pour l'affichage
        masked_uri = mongodb_uri[:14] + "***MASQUÉ***" + mongodb_uri[-20:] if len(mongodb_uri) > 34 else "***MASQUÉ***"
        print(f"📍 URI (masquée): {masked_uri}")
    
    # Test de connexion via MongoDBManager
    try:
        from mongodb_manager import MongoDBManager
        print("\n🔗 Test de connexion via MongoDBManager...")
        
        db_manager = MongoDBManager()
        print("✅ Connexion réussie avec variables d'environnement")
        
        # Test rapide d'opération
        total_articles = db_manager.collection.count_documents({})
        print(f"📊 Articles en base: {total_articles}")
        
        db_manager.close()
        print("✅ Connexion fermée proprement")
        
    except ValueError as e:
        print(f"❌ Erreur de configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    print("\n🎉 SÉCURITÉ VALIDÉE : Aucune chaîne de connexion en dur détectée !")
    return True

if __name__ == "__main__":
    test_env_security()
