import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval, get_geolocation
from ast import literal_eval

load_dotenv()

# --- Page config
st.set_page_config(
    page_title="💼 Job Market Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = "https://back-end-render-dg5f.onrender.com"

# --- Global CSS (sobre & épuré)
st.markdown("""
<style>
:root{
  --bg:#0b0d10;           /* page bg (Streamlit dark-friendly); keep white cards */
  --card-bg:#ffffff;
  --muted:#6b7280;
  --text:#0f172a;
  --primary:#2563eb;
  --primary-2:#1d4ed8;
  --border:#e5e7eb;
  --badge:#f1f5f9;
}
html, body, [data-testid="stAppViewContainer"]{
  background: var(--bg);
}
.main-header {
  background: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.75));
  backdrop-filter: blur(6px);
  padding: 28px 28px 20px;
  border-radius: 18px;
  border: 1px solid var(--border);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  margin-bottom: 20px;
}
.main-header h1{
  margin:0; padding:0; color: var(--text); letter-spacing: .2px;
}
.main-header p{
  margin:6px 0 0; color: var(--muted);
}
.section-title{
  font-weight:700; color: var(--text); margin: 8px 0 8px;
}
.metric-card, .job-card{
  background: var(--card-bg);
  border:1px solid var(--border);
  border-radius:16px;
  padding:14px 16px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.06);
}
.job-card h4{
  margin:0 0 8px 0; color: var(--text);
}
.job-meta{
  display:flex; flex-wrap:wrap; gap:10px; font-size: 0.93rem; color: var(--muted);
}
.badges{ display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }
.badge{
  background: var(--badge);
  border:1px solid var(--border);
  border-radius:999px;
  padding:6px 10px;
  font-size: 12.5px;
  color:#334155;
}
.stButton > button{
  background: var(--primary);
  color: #fff; font-weight: 600;
  border: 1px solid transparent;
  border-radius: 10px; padding: 8px 14px;
}
.stButton > button:hover{ background: var(--primary-2); }
.pager{
  display:flex; align-items:center; justify-content:space-between; gap:10px;
  margin-top: 8px;
}
.pager .info{
  flex:1; text-align:center; color: var(--muted); font-weight:600;
}
a.clean {
  color: var(--primary); text-decoration: none; font-weight: 600;
}
a.clean:hover{ text-decoration: underline; }
.sidebar-title{
  font-weight: 700; color:#e5e7eb; margin: 2px 0 8px;
}
</style>
""", unsafe_allow_html=True)

# --- Header
st.markdown("""
<div class="main-header">
  <h1>💼 Job Market Dashboard</h1>
  <p>Filtre, explore, clique. Le reste est du bruit.</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar (plus lisible)
st.sidebar.title("🧭 Navigation")
page = st.sidebar.selectbox("Choisis une page", ["👤 Profile", "📊 Power BI"])

# ---------- Utilities
def safe_list(x):
    if isinstance(x, list): return x
    if isinstance(x, str):
        try:
            v = literal_eval(x)
            return v if isinstance(v, list) else []
        except Exception:
            return []
    return []

def render_offer(offre: dict):
    title = offre.get("TITLE") or "Titre non disponible"
    ville = offre.get("VILLE") or "Non spécifié"
    region = offre.get("REGION") or "Région non spécifiée"
    contrat = offre.get("TYPE_CONTRAT") or "Non spécifié"
    url = offre.get("SOURCE_URL") or "#"
    skills = safe_list(offre.get("SKILLS", "[]"))

    st.markdown(f"""
    <div class="job-card">
        <h4>🎯 {title}</h4>
        <div class="job-meta">
            <div>📍 {ville} — {region}</div>
            <div>💼 {contrat}</div>
            <div>🔗 <a class="clean" href="{url}" target="_blank">Voir l'offre</a></div>
        </div>
        <div class="badges">
            {''.join([f'<span class="badge">{s}</span>' for s in skills[:10]])}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Pages
def show_candidate_profile():
    st.subheader("🎯 Filtres")
    if st.session_state.get("scroll_to_top", False):
        streamlit_js_eval(js_expressions=["window.scrollTo(0, 0)"])
        st.session_state.scroll_to_top = False

    if "page" not in st.session_state:
        st.session_state.page = 0
    limit = 20
    offset = st.session_state.page * limit

    # Fetch filters
    try:
        villes = [v[0] for v in requests.get(f"{API_BASE_URL}/candidat/ville", timeout=20).json()["data"]]
        departements = [d[0] for d in requests.get(f"{API_BASE_URL}/candidat/departement", timeout=20).json()["data"]]
        regions = [r[0] for r in requests.get(f"{API_BASE_URL}/candidat/region", timeout=20).json()["data"]]
        skills = [s["skill"] for s in requests.get(f"{API_BASE_URL}/skills/", timeout=20).json()]
        contrats = [c[0] for c in requests.get(f"{API_BASE_URL}/candidat/contrat", timeout=20).json()["data"]]
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return

    # Filters layout
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.markdown("<div class='section-title'>🏙️ Villes</div>", unsafe_allow_html=True)
        selected_villes = st.multiselect(" ", villes, label_visibility="collapsed")

        st.markdown("<div class='section-title'>🏞️ Départements</div>", unsafe_allow_html=True)
        selected_departements = st.multiselect("  ", departements, label_visibility="collapsed")

    with c2:
        st.markdown("<div class='section-title'>🌍 Régions</div>", unsafe_allow_html=True)
        selected_regions = st.multiselect("   ", regions, label_visibility="collapsed")

        st.markdown("<div class='section-title'>🧠 Compétences</div>", unsafe_allow_html=True)
        selected_skills = st.multiselect("    ", skills, label_visibility="collapsed")

    with c3:
        st.markdown("<div class='section-title'>📋 Contrats</div>", unsafe_allow_html=True)
        selected_contrats = st.multiselect("     ", contrats, label_visibility="collapsed")

        st.markdown("<div class='section-title'>🕒 Date de publication</div>", unsafe_allow_html=True)
        date_options = {
            "⏰ 24 dernières heures": "last_24h",
            "🗓️ 3 derniers jours": "last_3_days",
            "📆 7 derniers jours": "last_7_days",
        }
        selected_date_label = st.selectbox("      ", [""] + list(date_options.keys()), label_visibility="collapsed")

    search = st.button("🔍 Rechercher", type="primary")
    if search:
        st.session_state.page = 0

    # Build params
    params = []
    for v in selected_villes: params.append(("ville", v))
    for d in selected_departements: params.append(("departement", d))
    for r in selected_regions: params.append(("region", r))
    for s in selected_skills: params.append(("skill", s))
    for c in selected_contrats: params.append(("contrat", c))
    if selected_date_label:
        params.append(("date_filter", date_options[selected_date_label]))
    params += [("limit", limit), ("offset", offset)]

    # Query
    try:
        response = requests.get(f"{API_BASE_URL}/search", params=params, timeout=60)
        if response.status_code != 200:
            st.error(f"Erreur API: {response.status_code}")
            return
        data = response.json()
        offres = data.get("data", [])
        total_count = data.get("total_count", 0)
        total_pages = max((total_count + limit - 1) // limit, 1)

        st.markdown(f"**{total_count}** offres trouvées")
        st.divider()

        if not offres:
            st.warning("Aucune offre trouvée avec ces filtres.")
            return

        # Grid-like rendering (2 columns)
        colA, colB = st.columns(2, gap="large")
        for idx, offre in enumerate(offres):
            with (colA if idx % 2 == 0 else colB):
                render_offer(offre)
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Pagination
        st.markdown("<div class='pager'>", unsafe_allow_html=True)
        col_prev, col_mid, col_next = st.columns([1,3,1])
        with col_prev:
            if st.button("⬅️ Précédent", use_container_width=True, disabled=(st.session_state.page == 0)):
                st.session_state.page -= 1
                st.session_state.scroll_to_top = True
                st.rerun()
        with col_mid:
            st.markdown(f"<div class='info'>Page {st.session_state.page + 1} / {total_pages}</div>", unsafe_allow_html=True)
        with col_next:
            if st.button("Suivant ➡️", use_container_width=True, disabled=((st.session_state.page + 1) >= total_pages)):
                st.session_state.page += 1
                st.session_state.scroll_to_top = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Erreur lors de la recherche : {e}")

def show_projet2():
    st.subheader("📊 Dashboard Power BI")
    st.info("Astuce : clique sur l’icône plein écran en bas à droite de la viz.")
    powerbi_iframe = """
    <iframe title="Back-to-Basic" width="1100" height="720"
    src="https://app.powerbi.com/view?r=eyJrIjoiNjRkNjQ1ZjgtOWFjZS00ODhiLTg2MzktNmE5ZmJlYzdhMmFkIiwidCI6IjFjODA3N2YwLTY5MDItNDc1NC1hYzE4LTA4Zjc4ZjhlOTUxZSJ9"
    frameborder="0" allowFullScreen="true"></iframe>
    """
    components.html(powerbi_iframe, height=760, width=1100)

# --- Router
if page == "👤 Profile":
    show_candidate_profile()
else:
    show_projet2()
