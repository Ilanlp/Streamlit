import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval, get_geolocation
from streamlit_mermaid import st_mermaid


load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Job Market Dashboard",
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
    st.sidebar.title("Navigation")
    
    # Menu de navigation
    page = st.sidebar.radio(
        "Choisissez une page :",
        ["🗺️ Stack Technique","🧮 DataViz","👤 Espace Candidat"]
    )
    

    if page == "👤 Espace Candidat":
        show_candidate_profile()
    elif page == "🧮 DataViz":
        show_projet2()
    elif page == "🗺️ Stack Technique":
        show_stack()

def show_candidate_profile():
    """Page de profil candidat avec filtres et pagination"""
    st.title("Filtres géographiques")

    if st.session_state.get("scroll_to_top", False):
        streamlit_js_eval(js_expressions=["window.scrollTo(0, 0)"])
        st.session_state.scroll_to_top = False
    
    # Initialisation pagination
    if "page" not in st.session_state:
        st.session_state.page = 0
    limit = 20
    offset = st.session_state.page * limit

    # Récupération des données pour les dropdowns
    try:
        villes = [v[0] for v in requests.get(f"{API_BASE_URL}/candidat/ville").json()["data"]]
        departements = [d[0] for d in requests.get(f"{API_BASE_URL}/candidat/departement").json()["data"]]
        regions = [r[0] for r in requests.get(f"{API_BASE_URL}/candidat/region").json()["data"]]
        skills = [s["skill"] for s in requests.get(f"{API_BASE_URL}/skills/").json()]
        contrats = [c[0] for c in requests.get(f"{API_BASE_URL}/candidat/contrat").json()["data"]]
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return
    
    # Interface de filtres
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏙️ Villes")
        selected_villes = st.multiselect("Sélectionnez des villes", villes)

        st.subheader("🏞️ Départements")
        selected_departements = st.multiselect("Sélectionnez des départements", departements)

        st.subheader("🌍 Régions")
        selected_regions = st.multiselect("Sélectionnez des régions", regions)

    with col2:
        st.subheader("🧠 Skills")
        selected_skills = st.multiselect("Sélectionnez des compétences", skills)

        st.subheader("📋 Contrats")
        selected_contrats = st.multiselect("Sélectionnez des contrats", contrats)

        st.subheader("🕒 Date de publication")
        date_options = {
            "⏰ Dernières 24h": "last_24h",
            "🗓️ 3 derniers jours": "last_3_days",
            "📆 7 derniers jours": "last_7_days"
        }
        selected_date_label = st.selectbox("Filtrer par date", [""] + list(date_options.keys()))

    # Bouton de recherche
    if st.button("🔍 Rechercher", type="primary"):
        st.session_state.page = 0  # reset à la première page

    # Construction des paramètres
    params = []
    for v in selected_villes: params.append(("ville", v))
    for d in selected_departements: params.append(("departement", d))
    for r in selected_regions: params.append(("region", r))
    for s in selected_skills: params.append(("skill", s))
    for c in selected_contrats: params.append(("contrat", c))
    if selected_date_label:
        params.append(("date_filter", date_options[selected_date_label]))
    params.append(("limit", limit))
    params.append(("offset", offset))

    # Appel API
    try:
        response = requests.get(f"{API_BASE_URL}/search", params=params)
        if response.status_code == 200:
            data = response.json()
            offres = data.get("data", [])
            total_count = data.get("total_count", 0)
            total_pages = max((total_count + limit - 1) // limit, 1)

            if not offres:
                st.warning("Aucune offre trouvée.")
            else:
                st.subheader(f"📊 {total_count} offres trouvées – Page {st.session_state.page + 1} / {total_pages}")
                
                for i, offre in enumerate(offres, 1):
                    with st.container():
                        st.markdown(f"""
                            <div class="metric-card">
                                <h4>{offre.get('TITLE', 'Titre non disponible')}</h4>
                                <p><strong>📍 Lieu:</strong> {offre.get('VILLE', 'Non spécifié')} ({offre.get('REGION', 'Région non spécifiée')})</p>
                                <p><strong>💼 Contrat:</strong> {offre.get('TYPE_CONTRAT', 'Non spécifié')}</p>
                                <p><strong>🛠️ Compétences:</strong> {', '.join(eval(offre.get('SKILLS', '[]')))}</p>
                                <p><strong>🔗 Lien:</strong> <a href="{offre.get('SOURCE_URL', '#')}" target="_blank">Voir l'offre</a></p>
                            </div>
                        """, unsafe_allow_html=True)

                # Pagination UI
                col_prev, col_page, col_next = st.columns(3)
                with col_prev:
                    if st.button("⬅️ Page précédente") and st.session_state.page > 0:
                        st.session_state.page -= 1
                        st.session_state.scroll_to_top = True
                        st.rerun()
                with col_page:
                    st.markdown(f"<div style='text-align:center;font-weight:bold;'>📄 Page {st.session_state.page + 1} sur {total_pages}</div>", unsafe_allow_html=True)
                with col_next:
                    if st.button("➡️ Page suivante") and (st.session_state.page + 1) < total_pages:
                        st.session_state.page += 1
                        st.session_state.scroll_to_top = True
                        st.rerun()
        else:
            st.error(f"Erreur API: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Erreur lors de la recherche : {str(e)}")

def show_projet2():
    st.title("📊 DataViz - Marché de la Data 2025")
    st.markdown("Voici mon dashboard interactif Power BI intégré :")
    st.info("🔍 Pour profiter pleinement du dashboard, cliquez sur l’icône plein écran en bas à droite de la visualisation.")

    powerbi_iframe = """
    <iframe title="Back-to-Basic" width="800" height="600" 
    src="https://app.powerbi.com/view?r=eyJrIjoiNjRkNjQ1ZjgtOWFjZS00ODhiLTg2MzktNmE5ZmJlYzdhMmFkIiwidCI6IjFjODA3N2YwLTY5MDItNDc1NC1hYzE4LTA4Zjc4ZjhlOTUxZSJ9" 
    frameborder="0" allowFullScreen="true"></iframe>
    """

    # Affiche dans l'app Streamlit
    components.html(powerbi_iframe, height=1020, width=1020)

def show_stack():
    st.title("🗺️ Stack Technique du Projet")
    st.caption("Vue d’ensemble des outils utilisés et des flux de données.")

    mermaid_code = """
flowchart LR
  S[Sources (APIs, CSV, JSON)] --> PY[Python ETL]

  subgraph Orchestration
    AF[Airflow]
  end
  subgraph Versioning_CI_CD
    GH[GitHub]
  end
  subgraph Containers
    DK[Docker]
  end
  subgraph Data_Platform
    SN[(Snowflake Data Warehouse)]
    DBT[dbt Models / Tests]
  end
  subgraph Apps_and_Viz
    FA[FastAPI Backend]
    ST[Streamlit App]
    PBI[Power BI]
  end

  %% Pipelines
  PY -->|Load| SN
  AF -->|Schedule| PY
  AF -->|Schedule| DBT
  DBT -->|Transform| SN

  %% Data access
  FA -->|SQL / Views| SN
  ST -->|REST| FA
  PBI -->|Direct Query / Import| SN

  %% DevOps
  GH -->|Code / PR / Actions| DK
  DK -.->|Containerize| PY
  DK -.->|Containerize| FA
  DK -.->|Containerize| AF
"""
    st_mermaid(mermaid_code)



if __name__ == "__main__":
    main() 