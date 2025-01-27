import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration API corrigée
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/chains/solana"  # Nouvelle endpoint
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Paramètres
MIN_LIQUIDITY = 500  # Réduit pour plus de résultats
MAX_AGE_MINUTES = 10

def fetch_new_pairs():
    """Récupère les paires Solana avec nouvelle structure de données"""
    try:
        response = requests.get(DEXSCREENER_API, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        if response.status_code == 200:
            return process_pairs(response.json().get('pairs', []))
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur API: {str(e)}")
        return pd.DataFrame()

def process_pairs(pairs):
    """Traite les nouvelles paires avec gestion d'erreur améliorée"""
    processed = []
    
    for pair in pairs:
        try:
            created_at = datetime.fromtimestamp(pair['pairCreatedAt']/1000)
            age = (datetime.now() - created_at).total_seconds() / 60
            
            if age > MAX_AGE_MINUTES:
                continue
                
            processed.append({
                'Pair': f"{pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}",
                'Liquidity': pair['liquidity'].get('usd', 0),
                'Âge (min)': round(age, 1),
                'Volume 1h': pair['volume'].get('h1', 0),
                'Honeypot': pair.get('honeypot', False),
                'Lien': f"https://dexscreener.com/solana/{pair['pairAddress']}"
            })
        except KeyError as e:
            continue
            
    return pd.DataFrame(processed)

# Interface utilisateur
st.title("🔥 Solana Real-Time Sniper v2")

if 'running' not in st.session_state:
    st.session_state.running = False

# Contrôles
col1, col2, col3 = st.columns([1,1,2])
with col1:
    if st.button("🚀 Start" if not st.session_state.running else "🌀 Scanning..."):
        st.session_state.running = True
with col2:
    if st.button("🛑 Stop"):
        st.session_state.running = False
with col3:
    refresh_rate = st.slider("Refresh (sec)", 10, 300, 30)

# Boucle principale
placeholder = st.empty()
while st.session_state.running:
    with placeholder.container():
        try:
            df = fetch_new_pairs()
            
            if not df.empty:
                df = df[df['Liquidity'] > MIN_LIQUIDITY].sort_values('Âge (min)', ascending=True)
                
                # Affichage des données
                for _, row in df.iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        text = f"**{row['Pair']}** - Liquidité: ${row['Liquidity']:,.0f} - Âge: {row['Âge (min)']}min"
                        if row['Honeypot']:
                            st.error(f"🚨 {text} - HONEYPOT DETECTÉ!")
                        else:
                            st.success(f"✅ {text}")
                    with col2:
                        st.markdown(f"[📈 View]({row['Lien']})")
                
                st.write(f"🔍 {len(df)} nouvelles paires détectées")
            else:
                st.warning("Aucune nouvelle paire - vérifiez les paramètres de liquidité")
                
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
            st.session_state.running = False
            
        time.sleep(refresh_rate)
