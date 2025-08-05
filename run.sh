#!/bin/bash

echo "🚀 Lancement du Job Market Dashboard - Version Streamlit"
echo "=================================================="

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si les dépendances sont installées
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# Lancer l'application
echo "🌐 Lancement de l'application Streamlit..."
echo "📍 L'application sera accessible à l'adresse : http://localhost:8501"
echo "🔄 Appuyez sur Ctrl+C pour arrêter l'application"
echo ""

streamlit run main.py --server.port=8501 --server.address=0.0.0.0 