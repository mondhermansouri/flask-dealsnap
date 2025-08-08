# 🚀 Installation locale de DealSnap

Guide complet pour installer et lancer DealSnap sur votre machine locale.

## 📋 Prérequis

- **Python 3.8+** installé sur votre système
- **pip** (gestionnaire de paquets Python)
- **Git** (optionnel, pour cloner le projet)

### Vérifier Python

```bash
python --version
# ou
python3 --version
```

## 🛠️ Installation automatique

### Option 1: Installation rapide (recommandée)

```bash
# 1. Naviguer dans le dossier du projet
cd chemin/vers/dealsnap

# 2. Lancer le script de configuration automatique
python setup_local.py
```

### Option 2: Installation manuelle

Si l'installation automatique ne fonctionne pas:

```bash
# 1. Installer les dépendances Python
pip install Flask==3.0.0
pip install Flask-SQLAlchemy==3.1.1
pip install Flask-Login==0.6.3
pip install Flask-CORS==4.0.0
pip install Werkzeug==3.0.1
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install openai==1.3.0
pip install python-dotenv==1.0.0

# 2. Créer le fichier .env (voir section Configuration)
```

## ⚙️ Configuration

### Fichier .env

Créez un fichier `.env` dans le dossier racine avec ce contenu:

```env
# Base de données locale
DATABASE_URL=sqlite:///dealsnap_local.db

# Clé secrète pour les sessions
SESSION_SECRET=votre-cle-secrete-ici

# OpenAI API Key (optionnel)
OPENAI_API_KEY=sk-votre-cle-openai

# Configuration Flask
FLASK_DEBUG=True
FLASK_ENV=development
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

### Configuration OpenAI (optionnel)

1. Créez un compte sur [OpenAI](https://platform.openai.com/)
2. Générez une clé API
3. Ajoutez-la dans le fichier `.env`

**Note**: Sans clé OpenAI, l'app utilisera des titres prédéfinis.

## 🚀 Lancement

### Méthode 1: Script automatique

```bash
python run_local.py
```

### Méthode 2: Lancement manuel

```bash
python app_local.py
```

### Méthode 3: Flask CLI

```bash
export FLASK_APP=app_local.py
flask run --host=127.0.0.1 --port=5000 --debug
```

## 🌐 Accès à l'application

Une fois lancée, l'application sera disponible sur:

- **Site principal**: http://127.0.0.1:5000
- **Interface admin**: http://127.0.0.1:5000/admin
- **Inscription**: http://127.0.0.1:5000/register

## 👤 Premier accès

### 1. Créer un compte administrateur

1. Allez sur http://127.0.0.1:5000/register
2. Créez votre compte admin (seul le premier compte peut être créé)
3. Connectez-vous sur http://127.0.0.1:5000/login

### 2. Accéder au tableau de bord

1. Allez sur http://127.0.0.1:5000/admin
2. Vous verrez les deals d'exemple créés automatiquement
3. Utilisez "Add Deal" pour ajouter vos propres deals

## 📊 Fonctionnalités disponibles

### Interface publique
- Affichage des deals avec filtres par catégorie
- Deals en vedette
- Tracking des clics pour analytics
- Interface responsive (mobile/desktop)

### Interface administrateur
- Tableau de bord avec analytics
- Ajout manuel de deals
- Gestion des deals existants
- Génération de titres IA
- Scraping de deals par URL

### API REST
- `/api/deals` - Liste des deals
- `/api/deals/featured` - Deals en vedette
- `/api/deals/search` - Recherche
- `/api/analytics` - Statistiques

## 🔧 Gestion des données

### Base de données

La base de données SQLite est créée automatiquement dans `dealsnap_local.db`.

### Réinitialiser les données

```bash
# Supprimer la base de données
rm dealsnap_local.db

# Relancer l'application (base recréée automatiquement)
python run_local.py
```

## 🐛 Résolution de problèmes

### Port déjà utilisé

Si le port 5000 est occupé:

```bash
# Changer le port dans .env
FLASK_PORT=8080

# Ou lancer directement
python app_local.py --port 8080
```

### Erreurs de dépendances

```bash
# Mettre à jour pip
pip install --upgrade pip

# Réinstaller les dépendances
pip install --force-reinstall -r requirements.txt
```

### Problèmes de permissions

Sur macOS/Linux:

```bash
chmod +x run_local.py
chmod +x setup_local.py
```

## 📱 Développement mobile

### API pour application mobile

L'API REST est disponible pour développer une app mobile:

```bash
# Test de l'API
curl http://127.0.0.1:5000/api/deals
curl http://127.0.0.1:5000/api/deals/featured
```

### URLs importantes pour l'app mobile

- Base API: `http://127.0.0.1:5000/api/`
- Tracking clics: `http://127.0.0.1:5000/click/{deal_id}`

## 💰 Monétisation

### Configuration des liens d'affiliation

1. Inscrivez-vous aux programmes d'affiliation:
   - Amazon Associates
   - Best Buy Affiliate
   - Autres partenaires

2. Ajoutez vos liens d'affiliation dans les deals

3. Les clics sont trackés automatiquement pour vos analytics

## 🚀 Déploiement en production

Pour déployer en production, voir le fichier de configuration Replit ou adaptez pour:

- Heroku
- DigitalOcean
- Railway
- Autres plateformes cloud

## 📞 Support

En cas de problème:

1. Vérifiez les logs dans la console
2. Consultez la documentation des erreurs Flask
3. Assurez-vous que toutes les dépendances sont installées

**Version locale prête! 🎉**