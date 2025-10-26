import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
from datetime import datetime

# ===============================
# ⚡ CONFIGURATION DE BASE
# ===============================
SUPABASE_URL = "https://yourproject.supabase.co"
SUPABASE_KEY = "your-supabase-api-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Agent IA Énergie Cameroun", layout="wide")

# ===============================
# 🎨 EN-TÊTE
# ===============================
st.title("⚡ Agent IA Énergie Cameroun")
st.markdown("#### Tableau de bord de supervision énergétique")
st.markdown("---")

# ===============================
# 🗃️ CHARGEMENT DES DONNÉES
# ===============================
@st.cache_data(ttl=60)
def charger_donnees():
    data = supabase.table("pannes").select("*").order("date", desc=True).execute()
    return pd.DataFrame(data.data)

df = charger_donnees()

if df.empty:
    st.warning("Aucune donnée disponible pour le moment. Attendez quelques cycles N8N ⏳")
    st.stop()

# ===============================
# 📊 STATISTIQUES GLOBALES
# ===============================
col1, col2, col3, col4 = st.columns(4)
col1.metric("🔋 Total des relevés", len(df))
col2.metric("⚠️ Pannes détectées", len(df[df['status'] == 'panne']))
col3.metric("✅ États normaux", len(df[df['status'] == 'normal']))
col4.metric("📍 Postes surveillés", df['poste'].nunique())

st.markdown("---")

# ===============================
# 📅 GRAPHIQUE HEBDOMADAIRE
# ===============================
df['semaine'] = pd.to_datetime(df['date']).dt.to_period('W').astype(str)
hebdo = df[df['status'] == 'panne'].groupby('semaine')['id'].count().reset_index()
fig1 = px.bar(hebdo, x='semaine', y='id', title="📅 Évolution des pannes par semaine", color='id',
              labels={'id': 'Nombre de pannes', 'semaine': 'Semaine'})
st.plotly_chart(fig1, use_container_width=True)

# ===============================
# 📍 TOP 5 POSTES LES PLUS TOUCHÉS
# ===============================
top_postes = df[df['status'] == 'panne'].groupby('poste').size().reset_index(name='total').sort_values(by='total', ascending=False).head(5)
fig2 = px.bar(top_postes, x='poste', y='total', color='total', title="🏭 Top 5 des postes les plus touchés")
st.plotly_chart(fig2, use_container_width=True)

# ===============================
# 🌡️ MOYENNES DES 7 DERNIERS JOURS
# ===============================
recent = df[df['date'] >= (datetime.now() - pd.Timedelta(days=7)).strftime("%Y-%m-%d")]
moyennes = {
    "Tension moyenne (V)": round(recent['tension'].mean(), 2),
    "Courant moyen (A)": round(recent['courant'].mean(), 2),
    "Température moyenne (°C)": round(recent['temperature'].mean(), 2),
    "Fréquence moyenne (Hz)": round(recent['frequence'].mean(), 2)
}

st.subheader("📊 Moyennes des 7 derniers jours")
st.table(pd.DataFrame(list(moyennes.items()), columns=["Paramètre", "Valeur"]))

# ===============================
# 📅 TABLEAU DÉTAILLÉ DES PANNES
# ===============================
st.subheader("📋 Détails des pannes récentes")
st.dataframe(df[df['status'] == 'panne'][['poste', 'tension', 'courant', 'temperature', 'type_panne', 'date']].head(20))

# ===============================
# 🧭 PIED DE PAGE
# ===============================
st.markdown("---")
st.caption("© 2025 Agent IA Énergie Cameroun – conçu par MENYE BIBI Georges")
