#!/usr/bin/env python3
"""
Configuration script for DealSnap local environment
"""
import os
import sys
import subprocess
import sqlite3
from datetime import datetime

def install_dependencies():
    """Install required Python packages"""
    packages = [
        'Flask==3.0.0',
        'Flask-SQLAlchemy==3.1.1', 
        'Flask-Login==0.6.3',
        'Flask-CORS==4.0.0',
        'Werkzeug==3.0.1',
        'requests==2.31.0',
        'beautifulsoup4==4.12.2',
        'openai==1.3.0',
        'python-dotenv==1.0.0'
    ]
    
    print("🔧 Installation des dépendances Python...")
    for package in packages:
        print(f"Installation de {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"❌ Erreur lors de l'installation de {package}")
            return False
    
    print("✅ Toutes les dépendances sont installées!")
    return True

def create_env_file():
    """Create .env file with default configuration"""
    env_content = """# Configuration DealSnap Local
# Base de données locale
DATABASE_URL=sqlite:///dealsnap_local.db

# Clé secrète pour les sessions (changez-la en production)
SESSION_SECRET=dealsnap-local-secret-key-2024

# OpenAI API Key (optionnel - laissez vide pour utiliser les titres par défaut)
OPENAI_API_KEY=

# Mode debug (True pour développement)
FLASK_DEBUG=True
FLASK_ENV=development

# Host et port
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Fichier .env créé avec la configuration par défaut")
    else:
        print("ℹ️  Le fichier .env existe déjà")

def setup_database():
    """Initialize local database"""
    print("🗄️  Configuration de la base de données locale...")
    
    # Remove old database if exists
    if os.path.exists('dealsnap_local.db'):
        os.remove('dealsnap_local.db')
        print("🗑️  Ancienne base supprimée")
    
    # The database will be created automatically when the app starts
    print("✅ Base de données configurée")

def create_run_script():
    """Create run script for local development"""
    run_script = """#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the app
from app import app
import routes  # This imports all routes

if __name__ == '__main__':
    # Set Flask configuration
    app.config['DEBUG'] = True
    
    # Get host and port from env or use defaults
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"🚀 Démarrage de DealSnap sur http://{host}:{port}")
    print("📱 Interface Admin: http://127.0.0.1:5000/admin")
    print("🔐 Première connexion: http://127.0.0.1:5000/register")
    print("⚠️  Utilisez Ctrl+C pour arrêter le serveur")
    
    # Run the app
    app.run(
        host=host,
        port=port,
        debug=True,
        use_reloader=True
    )
"""
    
    with open('run_local.py', 'w') as f:
        f.write(run_script)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod('run_local.py', 0o755)
    
    print("✅ Script de lancement créé: run_local.py")

def main():
    """Main setup function"""
    print("🔥 Configuration de DealSnap pour environnement local")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Échec de l'installation des dépendances")
        return False
    
    # Create environment file
    create_env_file()
    
    # Setup database
    setup_database()
    
    # Create run script
    create_run_script()
    
    print("\n" + "=" * 50)
    print("🎉 Configuration terminée avec succès!")
    print("\n📋 Prochaines étapes:")
    print("1. Modifiez le fichier .env si nécessaire (OpenAI API key)")
    print("2. Lancez l'application: python run_local.py")
    print("3. Ouvrez http://127.0.0.1:5000 dans votre navigateur")
    print("4. Créez votre compte admin sur /register")
    print("\n💡 Conseils:")
    print("- Ajoutez votre clé OpenAI dans .env pour les titres IA")
    print("- Utilisez /admin pour gérer les deals")
    print("- Utilisez /admin/add-deal pour ajouter des deals manuellement")
    
    return True

if __name__ == '__main__':
    main()