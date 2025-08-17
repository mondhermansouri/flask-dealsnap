#!/usr/bin/env python3
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
