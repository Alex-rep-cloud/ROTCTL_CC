import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# 1. CONFIGURATION FORCÉE
st.set_page_config(page_title="Mission Control", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS AVANCÉ POUR LE PLEIN ÉCRAN RÉEL
st.markdown("""
    <style>
        /* Supprime les marges blanches autour du dashboard */
        .block-container { padding: 1rem 2rem !important; }
        [data-testid="stHeader"] { visibility: hidden; }
        
        /* Style des conteneurs de blocs */
        .control-block {
            background-color: #161b22;
            border: 1px solid #30363d;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        h3 { color: #58a6ff; font-size: 1.2rem !important; margin-bottom: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIMULATION DONNÉES ---
def get_data():
    return {
        "az": 210.4, "el": 45.2, "rssi": -102.5, 
        "lat": 48.85, "lon": 2.35, # Paris par défaut
        "status": "TRACKING ACTIVE"
    }

d = get_data()

# --- STRUCTURE EN 2 COLONNES PRINCIPALES ---
col_left, col_right = st.columns([1, 2.5]) # Gauche étroite, Droite large

# --- COLONNE DE GAUCHE (Empilement vertical) ---
with col_left:
    # BLOC 1 : ANTENNE & SIGNAL
    st.markdown('<div class="control-block">', unsafe_allow_html=True)
    st.subheader("📡 RF & ANTENNA")
    c1, c2 = st.columns(2)
    c1.metric("AZIMUT", f"{d['az']}°")
    c2.metric("ELEV", f"{d['el']}°")
    st.metric("SIGNAL STRENGTH", f"{d['rssi']} dBm", delta="2.1 dB")
    
    # Mini graph de signal
    sig_hist = pd.DataFrame(np.random.normal(-102, 1, size=(30, 1)))
    st.line_chart(sig_hist, height=120)
    st.markdown('</div>', unsafe_allow_html=True)

    # BLOC 2 : RECEPTION DATA
    st.markdown('<div class="control-block">', unsafe_allow_html=True)
    st.subheader("📥 DATA STREAM")
    logs = f"""[TIMESTAMP: {datetime.now().strftime('%M:%S')}]
[INFO] FRAME_SYNC_LOCKED
[DATA] BATT: 3.98V
[DATA] MODE: NOMINAL
[ERR] 0% PER"""
    st.code(logs, language="bash")
    st.markdown('</div>', unsafe_allow_html=True)

# --- COLONNE DE DROITE (CARTE) ---
with col_right:
    # On calcule la trace (historique + prédiction)
    trace_lat = [d['lat'] + i*2 for i in range(-5, 5)]
    trace_lon = [d['lon'] + i*5 for i in range(-5, 5)]

    fig = px.scatter_geo(lat=[d['lat']], lon=[d['lon']], 
                         projection="orthographic") # "orthographic" pour l'effet globe ou "natural earth"
    
    # Ajout de la ligne de trajectoire
    fig.add_trace(go.Scattergeo(
        lat=trace_lat, lon=trace_lon,
        mode='lines',
        line=dict(width=3, color='#00ff00')
    ))

    # Style sombre et zoom
    fig.update_geos(
        showcountries=True, countrycolor="#2f363d",
        showocean=True, oceancolor="#0d1117",
        showland=True, landcolor="#161b22",
        lataxis_range=[d['lat']-30, d['lat']+30], # Zoom dynamique autour du sat
        lonaxis_range=[d['lon']-60, d['lon']+60]
    )
    
    fig.update_layout(
        height=700, # Ajuste cette valeur selon la taille de ton écran
        margin={"r":0,"t":0,"l":0,"b":0},
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Refresh toutes les secondes
time.sleep(1)
st.rerun()