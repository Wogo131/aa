import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration de l'API DexScreener corrigée
DEXSCREENER_API = "https://api.dexscreener.com/token-profiles/latest/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Paramètres de surveillance
MIN_LIQUIDITY = 2000  # USD
MAX_AGE_MINUTES = 5    # Détecte les tokens de moins de 5 min

def fetch_new_pairs():
    """Récupère les nouvelles paires Solana avec analyse de sécurité"""
    try:
        response = requests.get(DEXSCREENER_API, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            return process_pairs(data.get('data', []))
        else:
            st.error(f"Erreur API: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Échec de la connexion: {str(e)}")
        return pd.DataFrame()

def process_pairs(data):
    """Traite les données de l'API"""
    pairs = []
    
    for item in data:
        created_at = datetime.fromtimestamp(item['createdAt']/1000)
        age = (datetime.now() - created_at).total_seconds() / 60
        
        if age > MAX_AGE_MINUTES:
            continue
            
        security_checks = {
            'honeypot': item.get('isHoneypot', False),
            'verified': item.get('isVerified', False),
            'lock': item.get('liquidityLocked', False)
        }
        
        pairs.append({
            'Pair': f"{item['baseToken']['symbol']}/{item['quoteToken']['symbol']}",
            'Liquidity': item['liquidity']['usd'],
            'Âge (min)': round(age, 1),
            'Volume 5m': item['volume']['h24'],
            'Security': security_checks,
            'Lien': f"https://dexscreener.com/solana/{item['pairAddress']}"
        })
    
    return pd.DataFrame(pairs)

# ... (le reste du code reste identique mais utilise ces nouvelles fonctions)

# Interface améliorée
st.title("🔫 Solana New Token Sniper Pro")
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stAlert {
        padding: 20px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Contrôle de surveillance
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Démarrer la surveillance", key="start"):
        st.session_state.running = True
with col2:
    if st.button("🛑 Arrêter la surveillance", key="stop"):
        st.session_state.running = False

# Boucle principale
if 'running' not in st.session_state:
    st.session_state.running = False

placeholder = st.empty()
refresh_rate = st.sidebar.slider("Fréquence de rafraîchissement (secondes)", 10, 300, 60)

while st.session_state.running:
    with placeholder.container():
        try:
            new_pairs = fetch_new_pairs()
            if not new_pairs.empty:
                filtered_pairs = new_pairs[new_pairs['Liquidity'] > MIN_LIQUIDITY]
                display_live_data(filtered_pairs)
            else:
                st.warning("Aucune nouvelle paire détectée - vérifiez dans 30s")
                
        except Exception as e:
            st.error(f"Erreur critique: {str(e)}")
            st.session_state.running = False
            
    time.sleep(refresh_rate)
