# TP BeautifulSoup4 - Scraper Blog du Modérateur

Ce projet implémente un scraper complet pour le site **Blog du Modérateur** en utilisant BeautifulSoup4, avec sauvegarde en MongoDB Atlas et interface web de recherche.

## 🎯 Objectifs du TP - ✅ TOUS COMPLÉTÉS

Le script extrait les éléments suivants pour chaque article :

1. ✅ **Titre de l'article**
2. ✅ **Image miniature (thumbnail) principale**  
3. ✅ **Sous-catégorie/catégorie**
4. ✅ **Résumé (extrait/chapô)**
5. ✅ **Date de publication au format AAAA-MM-JJ**
6. ✅ **Auteur de l'article**
7. ✅ **Contenu complet de l'article (nettoyé et formaté)**
8. ✅ **Dictionnaire des images présentes dans l'article**
9. ✅ **Sauvegarde en base MongoDB Atlas**

**Fonctionnalités bonus réalisées :**
- ✅ **Script de recherche par catégorie/sous-catégorie**
- ✅ **Front-end web pour recherches avancées**
- ✅ **Scraping multi-pages (30+ articles)**
- ✅ **Recherche par auteur et titre**
- ✅ **Interface console complète**

## 📁 Structure du projet

```
webscraping/
├── test.py                    # Script principal MongoDB local
├── scraper_multi_pages.py     # Scraper avancé 30+ articles (RECOMMANDÉ)
├── mongodb_manager.py         # Gestionnaire MongoDB Atlas
├── search_articles.py         # Interface console de recherche
├── app.py                     # Application Flask (front-end web)
├── test_recherche.py          # Script validation recherches
├── test_security.py           # Test sécurité variables d'environnement
├── scraper_simple.py          # Version simple (sauvegarde JSON)
├── templates/
│   └── index.html            # Interface web
├── .env                      # Configuration sécurisée (non versionné)
├── .env.example              # Exemple de configuration
├── .gitignore                # Fichiers à ignorer par Git
├── requirements.txt           # Dépendances Python
├── articles.json             # Données exportées (générées)
└── README.md                 # Ce fichier
```

## 🔗 Configuration MongoDB Atlas

Le projet utilise **MongoDB Atlas** (cloud) avec configuration sécurisée via fichier `.env`.

### 🔒 Configuration sécurisée

1. **Copiez le fichier d'exemple :**
```bash
cp .env.example .env
```

2. **Modifiez le fichier `.env` avec vos vraies informations :**
```bash
# Configuration MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
MONGODB_DATABASE=wscrap
MONGODB_COLLECTION=articles
```

3. **Le fichier `.env` est ignoré par Git** pour protéger vos credentials.

**Base de données :** `wscrap`  
**Collection :** `articles`

> ⚠️ **Sécurité :** Ne jamais commiter le fichier `.env` dans Git !

## 🚀 Installation et utilisation

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configuration MongoDB

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Modifier .env avec vos vraies informations MongoDB Atlas
# MONGODB_URI=mongodb+srv://votre_username:votre_password@cluster.mongodb.net/...
```

### 3. **RECOMMANDÉ : Scraper multi-pages (30+ articles)**

```bash
python scraper_multi_pages.py
```

Cette version :
- ✅ Extrait **30+ articles** automatiquement
- ✅ Explore 7 URLs différentes (accueil, SEO, réseaux sociaux, etc.)
- ✅ Sauvegarde directement en **MongoDB Atlas**
- ✅ Gestion de pagination automatique
- ✅ Évite les doublons
- ✅ Gestion d'erreurs robuste

### 3. Rechercher dans la base

**Interface console complète :**
```bash
python search_articles.py
```

**Test des fonctions de recherche :**
```bash
python test_recherche.py
```

**Test de sécurité des variables d'environnement :**
```bash
python test_security.py
```

### 4. Interface Web (Bonus)

```bash
python app.py
```

Puis ouvrir : `http://localhost:5000`

### 5. Autres options

**Version simple (sans MongoDB) :**
```bash
python scraper_simple.py
```

**Version MongoDB local :**
```bash
python test.py
```

## 🔍 Fonctionnalités de recherche - ✅ TOUTES VALIDÉES

### Interface console (`search_articles.py`)
- ✅ **Recherche par catégorie** (ex: "IA" → 15 articles)
- ✅ **Recherche par sous-catégorie**  
- ✅ **Recherche par auteur** (ex: "Alexandra Patard" → 2 articles)
- ✅ **Recherche par plage de dates**
- ✅ **Recherche dans les titres** (ex: "Google" → 6 articles)
- ✅ **Affichage des statistiques** (30 articles, 13 catégories, 10 auteurs)

### Interface web (`app.py`)
- ✅ Interface graphique moderne
- ✅ Recherches identiques à l'interface console
- ✅ Affichage des résultats avec preview
- ✅ Statistiques en temps réel

### Tests automatisés (`test_recherche.py`)
- ✅ Validation de toutes les fonctions de recherche
- ✅ Test de connexion MongoDB Atlas
- ✅ Vérification du nombre d'articles (30+)
- ✅ Tests de recherche par catégorie, titre et auteur

## 📊 Exemple de données extraites

```json
{
  "title": "Google va résumer les articles sur Discover",
  "thumbnail": "https://f.hellowork.com/blogdumoderateur/2025/07/discover-resume-ia-276x144.png",
  "subcategory": "Google",
  "summary": "Ces résumés générés par IA pourraient réduire...",
  "date": "2025-07-16",
  "author": "Thomas Coëffé",
  "content": "Des résumés générés par IA sur Discover...",
  "images": {
    "image_1": {
      "url": "https://...",
      "caption": "Capture d'écran Discover"
    }
  },
  "url": "https://www.blogdumoderateur.com/google-resumer-articles-discover/"
}
```

## 🛠️ Fonctionnalités techniques

### Multi-pages scraping
- ✅ **7 URLs explorées** (accueil, SEO, réseaux sociaux, IA, Google, etc.)
- ✅ **Pagination automatique** pour collecter plus d'articles
- ✅ **30+ articles garantis** en une seule exécution
- ✅ **Exploration intelligente** des différentes sections du site

### MongoDB Atlas
- ✅ **Connexion cloud sécurisée** via variables d'environnement
- ✅ **Aucune chaîne de connexion en dur** dans le code
- ✅ **Base wscrap** avec collection articles
- ✅ **Index optimisés** pour les recherches rapides
- ✅ **Éviter les doublons** (basé sur l'URL)
- ✅ **Timestamps** de création/modification
- ✅ **Fichier .env protégé** par .gitignore

### Gestion des images
- Détection automatique des attributs d'images (`src`, `data-src`, `data-lazy-src`)
- Extraction des légendes (alt, title)
- Stockage ordonné dans un dictionnaire

### Formatage du contenu
- Nettoyage automatique du HTML
- Suppression des caractères spéciaux
- Formatage cohérent des paragraphes
- Gestion de l'encodage UTF-8

### Gestion des dates
- Conversion automatique français → AAAA-MM-JJ
- Support des mois en français
- Gestion des erreurs de format

### Recherche avancée
- ✅ **Recherche insensible à la casse**
- ✅ **Expressions régulières** pour correspondances partielles
- ✅ **Recherche par catégorie/sous-catégorie**
- ✅ **Recherche par auteur et titre**
- ✅ **Statistiques détaillées**

## 🚨 Points d'attention

### Respect du site
- Headers User-Agent configurés
- Gestion des erreurs HTTP
- Pas de surcharge du serveur

### Robustesse
- Gestion des sélecteurs CSS multiples
- Fallbacks pour la détection d'auteur
- Validation des données extraites

## 🔧 Dépannage

### Configuration .env
```
Erreur: MONGODB_URI non trouvé dans les variables d'environnement
→ Copiez .env.example vers .env
→ Remplissez vos vraies informations MongoDB Atlas dans .env
→ Vérifiez que le fichier .env est dans le bon répertoire
```

### Erreur MongoDB Atlas
```
✅ RÉSOLU : MongoDB Atlas configuré et sécurisé
→ Connexion via variables d'environnement validée
→ Aucune chaîne de connexion en dur dans le code
→ Base wscrap avec 30+ articles opérationnelle
```

### Erreur de recherche
```
✅ RÉSOLU : Toutes les recherches fonctionnelles
→ Recherche par catégorie : ✅ (ex: 15 articles IA)
→ Recherche par titre : ✅ (ex: 6 articles Google)  
→ Recherche par auteur : ✅ (ex: 2 articles Alexandra Patard)
```

### Erreur de requête
```
Error: 403 Forbidden
→ Le site bloque parfois les requêtes automatisées
→ Headers User-Agent configurés pour éviter le blocage
→ Attendre quelques minutes entre les exécutions massives
```

### Erreur d'encodage
```
✅ GÉRÉ : Encodage UTF-8 automatique
→ Tous les caractères spéciaux français supportés
→ Accents et caractères spéciaux préservés
```

## 📈 Statut du projet

### ✅ TOUS LES OBJECTIFS ATTEINTS

**Fonctionnalités principales :**
- ✅ 9 éléments d'extraction requis pour le TP
- ✅ 30+ articles collectés et stockés
- ✅ MongoDB Atlas intégré et opérationnel
- ✅ Toutes les recherches fonctionnelles et validées

**Données actuelles :**
- **30 articles** en base de données
- **13 catégories** différentes identifiées  
- **10 auteurs** différents
- **Recherches validées** : catégorie (15 IA), titre (6 Google), auteur (2 Alexandra Patard)

**Interfaces disponibles :**
- ✅ Scraper multi-pages automatisé
- ✅ Interface console de recherche
- ✅ Interface web Flask
- ✅ Scripts de validation et test

### 🎯 Améliorations futures possibles

- [ ] Scraping programmé (cron jobs)
- [ ] Détection automatique de nouveaux articles
- [ ] Notifications de nouveaux contenus
- [ ] Export en différents formats (CSV, Excel)
- [ ] API REST complète
- [ ] Interface d'administration
- [ ] Mise en cache des résultats
- [ ] Analyse de sentiment sur les articles

## 👨‍💻 Auteur : 
Jokast Kassa

**Projet réalisé dans le cadre du TP BeautifulSoup4**  
Formation Web Scraping - Juillet 2025

### 🏆 Résultats du TP
- ✅ **TOUS les objectifs atteints**
- ✅ **MongoDB Atlas configuré et opérationnel**  
- ✅ **30+ articles extraits et stockés**
- ✅ **Toutes les recherches validées et fonctionnelles**
- ✅ **Interface web bonus implémentée**
- ✅ **Scripts de test et validation créés**

**État final :** Projet complet et prêt pour évaluation ✅
