import streamlit as st
import pandas as pd
import time
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="DEX Bot Manager",
    page_icon="🤖",
    layout="wide"
)

# Logo et titre
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2413/2413422.png", width=100)
with col2:
    st.title("Gestionnaire Automatisé de DEX")
    st.caption("Outils de surveillance de marchés décentralisés pour non-développeurs")

# Sidebar pour la configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    db_host = st.text_input("Adresse de la base de données", "localhost")
    db_port = st.number_input("Port", 5432)
    db_name = st.text_input("Nom de la base", "dexscreener")
    db_user = st.text_input("Utilisateur", "admin")
    db_password = st.text_input("Mot de passe", type="password")
    
    st.divider()
    
    min_liquidity = st.number_input("Liquidité minimale (USD)", 5000)
    min_age_days = st.number_input("Âge minimum (jours)", 3)
    
    st.divider()
    
    if st.button("🔁 Synchroniser les blacklists"):
        with st.spinner("Synchronisation en cours..."):
            time.sleep(2)
            st.success("Blacklists mises à jour !")

# Tableau de bord principal
tab1, tab2, tab3 = st.tabs(["📊 Surveillance", "🚨 Alertes", "⚖️ Blacklist"])

with tab1:
    st.subheader("Pairs Actives")
    
    # Faux données pour la démo
    sample_data = pd.DataFrame({
        'Pair': ['ETH/USDC', 'BTC/USDT', 'SOL/DAI'],
        'Liquidité (USD)': [15000, 22000, 8000],
        'Volume 24h': [4500, 7800, 1200],
        'Statut': ['✅ Sécurisé', '⚠️ A surveiller', '❌ Risqué']
    })
    
    st.dataframe(
        sample_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Liquidité (USD)": st.column_config.ProgressColumn(
                format="$%f",
                min_value=0,
                max_value=30000
            )
        }
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total en Surveillance", "$45,000", "+12%")
    with col2:
        st.metric("Alertes Actives", "3", "-2%")
    with col3:
        st.metric("Taux de Sécurité", "92%", "4%")

with tab2:
    st.subheader("Alertes Récentes")
    
    alerts = pd.DataFrame({
        'Date': ['2024-03-15 14:30', '2024-03-15 12:45', '2024-03-14 18:20'],
        'Pair': ['SUSPECT/ETH', 'RISKY/USDT', 'UNKNOWN/BTC'],
        'Raison': ['Liquidité suspecte', 'Adresse blacklistée', 'Volume anormal'],
        'Niveau': ['Haute', 'Critique', 'Moyenne']
    })
    
    st.dataframe(
        alerts,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Niveau": st.column_config.SelectboxColumn(
                options=["Basse", "Moyenne", "Haute", "Critique"]
            )
        }
    )

with tab3:
    st.subheader("Gestion des Blacklists")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Ajouter une entrée**")
        blacklist_type = st.selectbox("Type", ["Token", "Développeur"])
        address = st.text_input("Adresse")
        reason = st.text_area("Raison")
        
        if st.button("Ajouter à la blacklist"):
            if address and reason:
                st.success("Entrée ajoutée !")
            else:
                st.error("Remplissez tous les champs")
    
    with col2:
        st.write("**Liste actuelle**")
        blacklist = pd.DataFrame({
            'Adresse': ['0x123...def', '0x456...abc'],
            'Type': ['Token', 'Développeur'],
            'Raison': ['Scam connu', 'Activité suspecte']
        })
        
        st.dataframe(
            blacklist,
            use_container_width=True,
            hide_index=True
        )

# Contrôle principal
st.divider()
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("🚀 Démarrer la surveillance", type="primary"):
        with st.spinner("Surveillance en cours..."):
            time.sleep(2)
            st.toast("Surveillance active !", icon="✅")
    
    if st.button("🛑 Arrêter la surveillance"):
        st.toast("Surveillance arrêtée", icon="⚠️")