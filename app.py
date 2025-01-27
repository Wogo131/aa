import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration API corrigée selon la documentation officielle
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/chains/solana"  # Endpoint validé
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
}

# Paramètres optimisés
MIN_LIQUIDITY = 1000  # USD
MAX_AGE_MINUTES = 15

def fetch_new_pairs():
    """Récupère les paires avec gestion d'erreur améliorée"""
    try:
        response = requests.get(DEXSCREENER_API, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            return process_pairs(data.get('pairs', []))
        return pd.DataFrame()
    except requests.exceptions.HTTPError as e:
        st.error(f"Erreur API ({e.response.status_code}): {DEXSCREENER_API}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return pd.DataFrame()

def process_pairs(pairs):
    """Traite les données selon la structure officielle de l'API"""
    processed = []
    
    for pair in pairs:
        try:
            # Vérification des champs obligatoires
            if not all(key in pair for key in ['pairCreatedAt', 'baseToken', 'quoteToken', 'liquidity', 'volume']):
                continue
                
            created_at = datetime.fromtimestamp(pair['pairCreatedAt']/1000)
            age = (datetime.now() - created_at).total_seconds() / 60
            
            if age > MAX_AGE_MINUTES:
                continue
                
            processed.append({
                'Pair': f"{pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}",
                'Liquidity': pair['liquidity'].get('usd', 0),
                'Âge (min)': round(age, 1),
                'Volume 5m': pair['volume'].get('m5', 0),
                'Honeypot': pair.get('honeypot', False),
                'Verified': pair.get('info', {}).get('verified', False),
                'Lien': f"https://dexscreener.com/solana/{pair['pairAddress']}"
            })
        except KeyError as e:
            continue
            
    return pd.DataFrame(processed)

# Interface utilisateur améliorée
st.title("🚨 Solana Live Sniper v3.0")
st.caption("Surveillance en temps réel des nouveaux tokens Solana")

# Configuration sidebar
with st.sidebar:
    st.header("⚙️ Paramètres")
    MIN_LIQUIDITY = st.number_input("Liquidité minimale (USD)", 500, 10000, 1000)
    MAX_AGE_MINUTES = st.number_input("Âge maximum (minutes)", 1, 60, 15)
    refresh_rate = st.slider("Fréquence de rafraîchissement (sec)", 10, 300, 30)

# Contrôles principaux
col1, col2 = st.columns(2)
with col1:
    start_btn = st.button("🚀 Démarrer la surveillance", type="primary")
with col2:
    stop_btn = st.button("🛑 Arrêter la surveillance", type="secondary")

if start_btn:
    st.session_state.running = True
if stop_btn:
    st.session_state.running = False

# Boucle principale
if 'running' not in st.session_state:
    st.session_state.running = False

placeholder = st.empty()
error_count = 0

while st.session_state.running:
    with placeholder.container():
        try:
            df = fetch_new_pairs()
            
            if not df.empty:
                df = df[
                    (df['Liquidity'] > MIN_LIQUIDITY) & 
                    (df['Âge (min)'] <= MAX_AGE_MINUTES)
                ].sort_values('Âge (min)', ascending=True)
                
                # Affichage des résultats
                for _, row in df.iterrows():
                    with st.container(border=True):
                        cols = st.columns([3, 1, 1])
                        with cols[0]:
                            status = "🟢" if row['Verified'] else "🟡"
                            status = "🔴" if row['Honeypot'] else status
                            st.markdown(f"**{status} {row['Pair']}**  \n"
                                      f"Liquidité: ${row['Liquidity']:,.0f}  \n"
                                      f"Âge: {row['Âge (min)']}min")
                        with cols[1]:
                            st.metric("Volume 5m", f"${row['Volume 5m']:,.0f}")
                        with cols[2]:
                            st.markdown(f"[Ouvrir]({row['Lien']})")
                
                st.success(f"🔍 {len(df)} paires actives détectées")
                error_count = 0
            else:
                st.warning("Aucune nouvelle paire ne correspond aux critères")
                
        except Exception as e:
            error_count += 1
            st.error(f"Erreur temporaire ({error_count}/3 tentatives)")
            if error_count >= 3:
                st.session_state.running = False
                st.error("Trop d'erreurs - surveillance arrêtée")
            
        time.sleep(refresh_rate)
