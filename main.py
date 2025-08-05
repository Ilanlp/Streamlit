import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="💼 Job Market Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Variables globales
API_BASE_URL = "https://back-end-render-dg5f.onrender.com"

# CSS personnalisé pour un style moderne
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0d6efd, #6610f2);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stButton > button {
        background: linear-gradient(135deg, #0d6efd, #6610f2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0b5ed7, #5a0fd8);
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>💼 Job Market Dashboard</h1>
        <p>Explorez les données du marché de l'emploi en un clic</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation avec sidebar
    st.sidebar.title("🧭 Navigation")
    
    # Menu de navigation
    page = st.sidebar.selectbox(
        "Choisissez une page :",
        ["📍 Carte Villes / Régions + skills", "👤 Profile"]
    )
    
    if page == "📍 Carte Villes / Régions + skills":
        show_map_analysis()
    elif page == "👤 Profile":
        show_candidate_profile()

def get_map_figure(data, label_col):
    """Crée une carte avec Plotly Express"""
    df = pd.DataFrame(data)
    
    if df.empty:
        st.warning("Aucune donnée disponible pour cette sélection.")
        return None
    
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        size="count",
        hover_name=label_col,
        color=label_col,
        size_max=50,
        zoom=4,
        height=600,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="white",
    )
    return fig

def get_skill_figure(data):
    """Crée un graphique en barres pour les compétences"""
    df = pd.DataFrame(data)
    
    if df.empty:
        st.warning("Aucune donnée disponible pour les compétences.")
        return None
    
    fig = px.bar(
        df.sort_values("NB_OFFRES", ascending=False).head(20),
        x="NB_OFFRES",
        y="SKILL",
        orientation="h",
        title="Top Compétences Demandées sur le Marché",
        labels={"NB_OFFRES": "Nombre d'offres", "SKILL": "Compétence"},
        height=600
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin={"r": 10, "t": 40, "l": 80, "b": 40},
    )
    return fig

def show_map_analysis():
    """Page d'analyse des cartes et compétences"""
    st.title("🧭 Analyse du Marché de l'Emploi")
    
    # Sélecteur de vue
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        view_type = st.radio(
            "Choisissez le type d'analyse :",
            ["📍 Carte des zones", "💼 Top Compétences"],
            horizontal=True
        )
    
    if view_type == "📍 Carte des zones":
        st.subheader("Choisissez le niveau de regroupement géographique :")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            zone_type = st.radio(
                "Niveau géographique :",
                ["🧭 Villes", "🗺️ Département", "🗺️ Régions"],
                horizontal=False
            )
        
        # Mapping des sélections
        zone_mapping = {
            "🧭 Villes": "ville",
            "🗺️ Département": "departement", 
            "🗺️ Régions": "region"
        }
        
        selected_zone = zone_mapping[zone_type]
        
        try:
            if selected_zone == "ville":
                response = requests.get(f"{API_BASE_URL}/top_ville")
            elif selected_zone == "departement":
                response = requests.get(f"{API_BASE_URL}/top_departement")
            else:
                response = requests.get(f"{API_BASE_URL}/top_region")
            
            if response.status_code == 200:
                data = response.json()["data"]
                fig = get_map_figure(data, label_col=selected_zone)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Erreur API: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Erreur de chargement : {str(e)}")
    
    elif view_type == "💼 Top Compétences":
        try:
            response = requests.get(f"{API_BASE_URL}/top_skills")
            if response.status_code == 200:
                data = response.json()["data"]
                fig = get_skill_figure(data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Erreur API: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Erreur de chargement : {str(e)}")

def show_candidate_profile():
    """Page de profil candidat avec filtres"""
    st.title("🎯 Filtres géographiques")
    
    # Récupération des données pour les dropdowns
    try:
        # Villes
        villes_response = requests.get(f"{API_BASE_URL}/candidat/ville")
        villes = [v[0] for v in villes_response.json()["data"]] if villes_response.status_code == 200 else []
        
        # Départements
        departements_response = requests.get(f"{API_BASE_URL}/candidat/departement")
        departements = [d[0] for d in departements_response.json()["data"]] if departements_response.status_code == 200 else []
        
        # Régions
        regions_response = requests.get(f"{API_BASE_URL}/candidat/region")
        regions = [r[0] for r in regions_response.json()["data"]] if regions_response.status_code == 200 else []
        
        # Skills
        skills_response = requests.get(f"{API_BASE_URL}/skills/")
        skills = [s["skill"] for s in skills_response.json()] if skills_response.status_code == 200 else []
        
        # Contrats
        contrat_response = requests.get(f"{API_BASE_URL}/candidat/contrat")
        contrats = [c[0] for c in contrat_response.json()["data"]] if contrat_response.status_code == 200 else []
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return
    
    # Interface de filtres
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏙️ Villes")
        selected_villes = st.multiselect(
            "Sélectionnez une ou plusieurs villes",
            options=villes,
            placeholder="Choisissez des villes..."
        )
        
        st.subheader("🏞️ Départements")
        selected_departements = st.multiselect(
            "Sélectionnez un ou plusieurs départements",
            options=departements,
            placeholder="Choisissez des départements..."
        )
        
        st.subheader("🌍 Régions")
        selected_regions = st.multiselect(
            "Sélectionnez une ou plusieurs régions",
            options=regions,
            placeholder="Choisissez des régions..."
        )
    
    with col2:
        st.subheader("🧠 Skills")
        selected_skills = st.multiselect(
            "Sélectionnez une ou plusieurs compétences",
            options=skills,
            placeholder="Choisissez des compétences..."
        )
        
        st.subheader("📋 Contrats")
        selected_contrats = st.multiselect(
            "Sélectionnez un ou plusieurs types de contrat",
            options=contrats,
            placeholder="Choisissez des contrats..."
        )
    
    # Bouton de recherche
    if st.button("🔍 Rechercher", type="primary"):
        # Préparation des paramètres
        params = []
        
        if selected_villes:
            for v in selected_villes:
                params.append(("ville", v))
        if selected_departements:
            for d in selected_departements:
                params.append(("departement", d))
        if selected_regions:
            for r in selected_regions:
                params.append(("region", r))
        if selected_skills:
            for s in selected_skills:
                params.append(("skill", s))
        if selected_contrats:
            for c in selected_contrats:
                params.append(("contrat", c))
        
        try:
            response = requests.get(f"{API_BASE_URL}/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data or not data.get("data"):
                    st.warning("Aucune offre trouvée.")
                else:
                    offres = data["data"]
                    
                    st.subheader(f"📊 Résultats de recherche ({len(offres)} offres trouvées)")
                    
                    # Affichage des résultats
                    for i, offre in enumerate(offres, 1):
                        with st.container():
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🎯 {offre.get('TITLE', 'Titre non disponible')}</h4>
                                <p><strong>📍 Lieu:</strong> {offre.get('VILLE', 'Non spécifié')} ({offre.get('REGION', 'Région non spécifiée')})</p>
                                <p><strong>💼 Contrat:</strong> {offre.get('TYPE_CONTRAT', 'Non spécifié')}</p>
                                <p><strong>🛠️ Compétences:</strong> {', '.join(eval(offre.get('SKILLS', '[]')))}</p>
                                <p><strong>🔗 Lien:</strong> <a href="{offre.get('SOURCE_URL', '#')}" target="_blank">Voir l'offre</a></p>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.error(f"Erreur API: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Erreur lors de la recherche : {str(e)}")

if __name__ == "__main__":
    main() 