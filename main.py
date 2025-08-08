import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os, base64
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval, get_geolocation
from streamlit_mermaid import st_mermaid
from ast import literal_eval

load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Job Market Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Variables globales
API_BASE_URL = "https://back-end-render-dg5f.onrender.com"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(BASE_DIR, "logos")  # <— plus de dépendance au cwd

# CSS
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

# ---------- Utils
def _data_uri(path: str) -> str:
    """Retourne une data URI base64 pour embarquer l'image dans le SVG."""
    ext = os.path.splitext(path)[1].lower()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Logo introuvable: {path}")
    mime = "image/png" if ext == ".png" else "image/svg+xml"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def safe_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            v = literal_eval(x)
            return v if isinstance(v, list) else []
        except Exception:
            return []
    return []

# ---------- Pages
def main():
    # En-tête
    st.markdown("""
    <div class="main-header">
        <h1>💼 Job Market Dashboard</h1>
        <p>Explorez les données du marché de l'emploi en un clic</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choisissez une page :",
        ["🗺️ Stack Technique (Logos)", "🗺️ Stack Technique (Mermaid)", "🧮 DataViz", "👤 Espace Candidat"]
    )

    if page == "👤 Espace Candidat":
        show_candidate_profile()
    elif page == "🧮 DataViz":
        show_projet2()
    elif page == "🗺️ Stack Technique (Mermaid)":
        show_stack_mermaid()
    elif page == "🗺️ Stack Technique (Logos)":
        show_stack_logos()

def show_candidate_profile():
    """Page de profil candidat avec filtres et pagination"""
    st.title("Filtres géographiques")

    if st.session_state.get("scroll_to_top", False):
        streamlit_js_eval(js_expressions=["window.scrollTo(0, 0)"])
        st.session_state.scroll_to_top = False

    # Pagination
    if "page" not in st.session_state:
        st.session_state.page = 0
    limit = 20
    offset = st.session_state.page * limit

    # Dropdown data
    try:
        villes = [v[0] for v in requests.get(f"{API_BASE_URL}/candidat/ville", timeout=20).json()["data"]]
        departements = [d[0] for d in requests.get(f"{API_BASE_URL}/candidat/departement", timeout=20).json()["data"]]
        regions = [r[0] for r in requests.get(f"{API_BASE_URL}/candidat/region", timeout=20).json()["data"]]
        skills = [s["skill"] for s in requests.get(f"{API_BASE_URL}/skills/", timeout=20).json()]
        contrats = [c[0] for c in requests.get(f"{API_BASE_URL}/candidat/contrat", timeout=20).json()["data"]]
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return

    # Filtres UI
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

    # Rechercher
    if st.button("🔍 Rechercher", type="primary"):
        st.session_state.page = 0  # reset à la première page

    # Params
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

    # API call
    try:
        response = requests.get(f"{API_BASE_URL}/search", params=params, timeout=60)
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
                    skills_list = safe_list(offre.get('SKILLS', '[]'))
                    with st.container():
                        st.markdown(f"""
                            <div class="metric-card">
                                <h4>{offre.get('TITLE', 'Titre non disponible')}</h4>
                                <p><strong>📍 Lieu:</strong> {offre.get('VILLE', 'Non spécifié')} ({offre.get('REGION', 'Région non spécifiée')})</p>
                                <p><strong>💼 Contrat:</strong> {offre.get('TYPE_CONTRAT', 'Non spécifié')}</p>
                                <p><strong>🛠️ Compétences:</strong> {', '.join(skills_list[:10])}</p>
                                <p><strong>🔗 Lien:</strong> <a href="{offre.get('SOURCE_URL', '#')}" target="_blank">Voir l'offre</a></p>
                            </div>
                        """, unsafe_allow_html=True)

                # Pagination
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
    components.html(powerbi_iframe, height=1020, width=1020)


def show_stack_logos():
    st.title("🗺️ Stack Technique du Projet (Logos)")
    st.caption("Diagramme SVG avec logos embarqués.")

    with st.expander("🧪 Debug logos"):
        st.write("BASE_DIR:", BASE_DIR)
        st.write("LOGO_DIR:", LOGO_DIR)
        try:
            st.write("Contenu LOGO_DIR:", os.listdir(LOGO_DIR))
        except Exception as e:
            st.error(f"listdir failed: {e}")


    # chemins logos
    logos = {
        "sources":  os.path.join(LOGO_DIR, "sources.png"),
        "python":   os.path.join(LOGO_DIR, "python.png"),
        "airflow":  os.path.join(LOGO_DIR, "airflow.png"),
        "dbt":      os.path.join(LOGO_DIR, "dbt.png"),
        "snowflake":os.path.join(LOGO_DIR, "snowflake.png"),
        "docker":   os.path.join(LOGO_DIR, "docker.png"),
        "github":   os.path.join(LOGO_DIR, "github.png"),
        "fastapi":  os.path.join(LOGO_DIR, "fastapi.png"),
        "streamlit":os.path.join(LOGO_DIR, "streamlit.png"),
        "powerbi":  os.path.join(LOGO_DIR, "powerbi.png"),
    }
    try:
        data = {k: _data_uri(v) for k, v in logos.items()}
    except Exception as e:
        st.error(f"⚠️ Problème de logos : {e}")
        st.info("Assure-toi d’avoir tous les fichiers dans assets/logos/ (voir liste en haut).")
        return

    svg = f"""
<svg viewBox="0 0 1100 650" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;background:#0b0d10;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#9CA3AF"></path>
    </marker>
    <style><![CDATA[
      .label {{ fill:#e5e7eb; font: 600 14px system-ui, -apple-system, Segoe UI, Roboto; }}
      .sublabel {{ fill:#9ca3af; font: 500 12px system-ui; }}
      .box {{ fill:#111827; stroke:#374151; stroke-width:1.2; rx:16; }}
      .link {{ stroke:#9CA3AF; stroke-width:2.2; fill:none; }}
    ]]></style>
  </defs>

  <!-- Zones -->
  <rect x="40"  y="260" width="170" height="120" class="box"/>
  <rect x="260" y="260" width="170" height="120" class="box"/>
  <rect x="500" y="220" width="220" height="200" class="box"/>
  <rect x="820" y="180" width="230" height="320" class="box"/>
  <rect x="520" y="60"  width="540" height="90"  class="box"/>

  <text x="50"  y="252" class="sublabel">Sources</text>
  <text x="270" y="252" class="sublabel">ETL</text>
  <text x="510" y="212" class="sublabel">Data Warehouse & Transform</text>
  <text x="830" y="172" class="sublabel">Apps & Viz</text>
  <text x="530" y="52"  class="sublabel">Orchestration, CI/CD & Containers</text>

  <!-- Logos + labels -->
  <image href="{data['sources']}" x="90" y="285" width="80" height="80"/>
  <text x="125" y="385" text-anchor="middle" class="label">APIs / CSV / JSON</text>

  <image href="{data['python']}" x="310" y="285" width="80" height="80"/>
  <text x="345" y="385" text-anchor="middle" class="label">Python ETL</text>

  <image href="{data['snowflake']}" x="555" y="245" width="110" height="110"/>
  <text x="615" y="370" text-anchor="middle" class="label">Snowflake DW</text>

  <image href="{data['dbt']}" x="535" y="120" width="70" height="70"/>
  <text x="570" y="205" text-anchor="middle" class="label">dbt</text>

  <image href="{data['airflow']}" x="625" y="115" width="80" height="80"/>
  <text x="665" y="205" text-anchor="middle" class="label">Airflow</text>

  <image href="{data['github']}" x="760" y="95" width="60" height="60"/>
  <text x="790" y="165" text-anchor="middle" class="label">GitHub</text>

  <image href="{data['docker']}" x="835" y="95" width="70" height="60"/>
  <text x="870" y="165" text-anchor="middle" class="label">Docker</text>

  <image href="{data['fastapi']}" x="860" y="210" width="80" height="80"/>
  <text x="900" y="305" text-anchor="middle" class="label">FastAPI</text>

  <image href="{data['streamlit']}" x="860" y="320" width="80" height="80"/>
  <text x="900" y="415" text-anchor="middle" class="label">Streamlit</text>

  <image href="{data['powerbi']}" x="860" y="430" width="80" height="80"/>
  <text x="900" y="525" text-anchor="middle" class="label">Power BI</text>

  <!-- Flèches -->
  <path class="link" marker-end="url(#arrow)" d="M 210 320 C 230 320, 260 320, 260 320"/>
  <path class="link" marker-end="url(#arrow)" d="M 430 320 C 470 320, 520 320, 555 300"/>

  <path class="link" marker-end="url(#arrow)" d="M 575 190 C 580 210, 590 230, 610 240"/>
  <path class="link" marker-end="url(#arrow)" d="M 660 190 C 650 210, 640 230, 630 240"/>
  <path class="link" marker-end="url(#arrow)" d="M 660 190 C 630 240, 470 300, 430 320"/>

  <path class="link" marker-end="url(#arrow)" d="M 665 300 C 760 300, 820 300, 860 250"/>
  <path class="link" marker-end="url(#arrow)" d="M 900 290 C 900 330, 900 330, 900 350"/>
  <path class="link" marker-end="url(#arrow)" d="M 665 320 C 760 380, 820 440, 860 470"/>

  <path class="link" marker-end="url(#arrow)" d="M 790 125 C 760 125, 720 140, 710 155"/>
  <path class="link" marker-end="url(#arrow)" d="M 870 125 C 820 160, 680 170, 660 185"/>
  <path class="link" marker-end="url(#arrow)" d="M 870 125 C 760 150, 600 170, 560 185"/>
  <path class="link" marker-end="url(#arrow)" d="M 870 125 C 680 150, 420 230, 360 280"/>
</svg>
"""
    components.html(png, height=720*5, scrolling=False)

# Run
if __name__ == "__main__":
    main()
