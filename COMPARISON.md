# 🔄 Comparaison Dash vs Streamlit

## 📊 Structure générale

### Dash (Original)
```python
# Structure modulaire avec pages
app = dash.Dash(__name__, use_pages=True)
# Navigation avec dbc.Nav
# Pages séparées dans dossier pages/
```

### Streamlit (Nouveau)
```python
# Application monolithique avec sidebar
st.sidebar.selectbox() pour la navigation
# Toutes les fonctions dans main.py
```

## 🎨 Interface utilisateur

### Dash
- **Navigation** : `dbc.Nav` avec onglets
- **Layout** : `html.Div` avec CSS personnalisé
- **Style** : Bootstrap + CSS inline
- **Responsive** : Automatique avec Bootstrap

### Streamlit
- **Navigation** : `st.sidebar.selectbox()`
- **Layout** : `st.columns()`, `st.container()`
- **Style** : CSS personnalisé via `st.markdown()`
- **Responsive** : Automatique avec Streamlit

## 📍 Page "Carte Villes / Régions + skills"

### Dash
```python
# Radio buttons pour sélection
dcc.RadioItems(id="view-selector")
dcc.RadioItems(id="zone-selector")
# Callbacks pour mise à jour
@dash.callback(Output("dynamic-content", "children"), Input("view-selector", "value"))
```

### Streamlit
```python
# Radio buttons Streamlit
st.radio("Choisissez le type d'analyse :", options)
st.radio("Niveau géographique :", options)
# Mise à jour automatique (pas de callbacks)
```

## 👤 Page "Profile"

### Dash
```python
# Dropdowns avec dcc.Dropdown
dcc.Dropdown(id="ville-dropdown", multi=True)
# Bouton avec html.Button
html.Button("🔍 Rechercher", id="search-button")
# Callback pour recherche
@callback(Output("search-results", "children"), Input("search-button", "n_clicks"))
```

### Streamlit
```python
# Multiselect Streamlit
st.multiselect("Sélectionnez des villes", options)
# Bouton Streamlit
st.button("🔍 Rechercher", type="primary")
# Exécution directe (pas de callback)
```

## 🗺️ Visualisations

### Dash
```python
# Graphiques avec dcc.Graph
dcc.Graph(figure=fig)
# Carte avec plotly.express
px.scatter_mapbox()
```

### Streamlit
```python
# Graphiques avec st.plotly_chart
st.plotly_chart(fig, use_container_width=True)
# Même plotly.express pour les cartes
px.scatter_mapbox()
```

## 🔧 Avantages Streamlit

1. **Simplicité** : Moins de code, pas de callbacks
2. **Développement rapide** : Interface plus intuitive
3. **Mise à jour automatique** : Pas besoin de gérer les états
4. **Sidebar native** : Navigation intégrée
5. **Déploiement facile** : Streamlit Cloud, Heroku, etc.

## 🔧 Avantages Dash

1. **Flexibilité** : Plus de contrôle sur l'interface
2. **Performance** : Callbacks optimisés
3. **Écosystème** : Plus de composants disponibles
4. **Modularité** : Structure en pages séparées
5. **Bootstrap** : Design system complet

## 📁 Structure des fichiers

### Dash
```
frontend/
├── dash_app.py          # App principale
├── pages/
│   ├── top_ville.py     # Page carte
│   └── candidat.py      # Page profil
├── requirements.txt
└── Dockerfile.dash
```

### Streamlit
```
frontend2/
├── main.py              # App complète
├── requirements.txt
├── Dockerfile
├── .streamlit/
│   └── config.toml      # Configuration
├── run.sh               # Script de lancement
└── README.md
```

## 🚀 Lancement

### Dash
```bash
cd frontend
python dash_app.py
# Accès : http://localhost:8080
```

### Streamlit
```bash
cd frontend2
./run.sh
# ou
streamlit run main.py
# Accès : http://localhost:8501
``` 