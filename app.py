import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration de l'API DexScreener
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/chains/solana"

# Paramètres de surveillance
MIN_LIQUIDITY = 2000  # USD
MAX_AGE_MINUTES = 5   # Détecte les tokens de moins de 5 min

def fetch_new_pairs():
    """Récupère les nouvelles paires Solana avec analyse de sécurité"""
    response = requests.get(DEXSCREENER_API)
    data = response.json()
    
    pairs = []
    for pair in data['pairs']:
        created_at = datetime.fromtimestamp(pair['pairCreatedAt']/1000)
        age = (datetime.now() - created_at).total_seconds() / 60
        
        if age > MAX_AGE_MINUTES:
            continue
            
        security_checks = {
            'honeypot': pair.get('honeypot', False),
            'lock': pair['liquidity']['lock'] if 'lock' in pair['liquidity'] else False,
            'verified': pair['info'].get('verified', False)
        }
        
        pairs.append({
            'Pair': f"{pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}",
            'Liquidity': pair['liquidity']['usd'],
            'Âge (min)': round(age, 1),
            'Volume 5m': pair['volume']['m5'],
            'Security': security_checks,
            'Lien': f"https://dexscreener.com/solana/{pair['pairAddress']}"
        })
    
    return pd.DataFrame(pairs)

def display_live_data(df):
    """Affiche les données avec mise en forme dynamique"""
    st.subheader("🚨 Nouveaux Tokens Solana (Dernières 5min)")
    
    # Tri par liquidité et âge
    df = df.sort_values(by=['Liquidity', 'Âge (min)'], ascending=[False, True])
    
    # Création des colonnes
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.write("**Pairs Detected**")
        for _, row in df.iterrows():
            pair_text = f"{row['Pair']} - {row['Liquidity']:,.0f}$"
            if row['Security']['honeypot']:
                st.error(f"🔴 {pair_text} (Honeypot!)")
            elif row['Security']['verified']:
                st.success(f"🟢 {pair_text} (Verified)")
            else:
                st.warning(f"🟡 {pair_text}")

    with col2:
        st.write("**Security Analysis**")
        st.metric("Total Scam Detected", 
                 df[df['Security']['honeypot']].shape[0],
                 delta_color="off")
        
        st.progress(df[df['Security']['verified']].shape[0]/len(df))

    with col3:
        st.write("**Quick Actions**")
        if st.button("🔄 Refresh Data"):
            st.experimental_rerun()
            
        selected = st.selectbox("Pair Details", df['Pair'])
        selected_row = df[df['Pair'] == selected].iloc[0]
        st.markdown(f"[Open in DexScreener]({selected_row['Lien']})")

# Interface principale
st.title("🦖 Solana New Token Sniper")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 10, 300, 60)

placeholder = st.empty()
while True:
    with placeholder.container():
        try:
            new_pairs = fetch_new_pairs()
            filtered_pairs = new_pairs[new_pairs['Liquidity'] > MIN_LIQUIDITY]
            
            if not filtered_pairs.empty:
                display_live_data(filtered_pairs)
            else:
                st.warning("Aucun nouveau token détecté - vérifiez dans 30s")
                
        except Exception as e:
            st.error(f"Erreur de connexion à l'API: {str(e)}")
            
    time.sleep(refresh_rate)
