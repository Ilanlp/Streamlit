# 💼 Job Market Dashboard - Version Streamlit

Cette application Streamlit est une version équivalente du dashboard Dash original, offrant les mêmes fonctionnalités avec une interface moderne et intuitive.

## 🚀 Fonctionnalités

### 📍 Page "Carte Villes / Régions + skills"
- **Carte interactive** : Visualisation géographique des offres d'emploi
  - Niveau Ville
  - Niveau Département  
  - Niveau Région
- **Top Compétences** : Graphique en barres des compétences les plus demandées

### 👤 Page "Profile"
- **Filtres avancés** :
  - Sélection multiple de villes
  - Sélection multiple de départements
  - Sélection multiple de régions
  - Sélection multiple de compétences
  - Sélection multiple de types de contrat
- **Recherche d'offres** : Résultats détaillés avec liens directs

## 🛠️ Installation

### Option 1 : Installation locale
```bash
cd frontend2
pip install -r requirements.txt
streamlit run main.py
```

### Option 2 : Avec Docker
```bash
cd frontend2
docker build -t job-market-streamlit .
docker run -p 8501:8501 job-market-streamlit
```

## 🌐 Accès
L'application sera accessible à l'adresse : `http://localhost:8501`

## 📋 Prérequis
- Python 3.9+
- Backend API accessible sur `http://localhost:8000`
- Connexion internet pour les cartes interactives

## 🎨 Interface
- Design moderne avec dégradés
- Navigation intuitive via sidebar
- Responsive design
- Cartes interactives avec Plotly
- Filtres multi-sélection

## 🔧 Configuration
L'URL de l'API backend peut être modifiée dans le fichier `main.py` :
```python
API_BASE_URL = "http://localhost:8000"
``` 