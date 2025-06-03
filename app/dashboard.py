import streamlit as st
import overview_tab
import search_tab
import cluster_tab
import relations_tab
import trends_tab

st.set_page_config(
    page_title="Système d'Analyse de Publications Scientifiques",
    layout="wide"
)

# Ajout Font Awesome pour les icônes
st.markdown("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .main-title {
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
        }
        .subtitle {
            font-size: 18px;
            color: #7f8c8d;
            margin-bottom: 20px;
        }
    </style>
    <div class='main-title'><i class="fas fa-microscope"></i> Système d'Analyse de Publications Scientifiques</div>
    <div class='subtitle'>Explorez, recherchez et visualisez les publications scientifiques extraites depuis arXiv et PubMed</div>
""", unsafe_allow_html=True)

# Pages disponibles avec noms personnalisés
pages = {
    " 𝐕𝐮𝐞 𝐝'𝐞𝐧𝐬𝐞𝐦𝐛𝐥𝐞": "Overview",
    " 𝐑𝐞𝐜𝐡𝐞𝐫𝐜𝐡𝐞 𝐚𝐯𝐚𝐧𝐜𝐞𝐞": "Recherche",
    " 𝐂𝐥𝐮𝐬𝐭𝐞𝐫𝐬 𝐭𝐡𝐞𝐦𝐚𝐭𝐢𝐪𝐮𝐞𝐬": "Clusters",
    " 𝐑𝐞𝐥𝐚𝐭𝐢𝐨𝐧𝐬 𝐬𝐜𝐢𝐞𝐧𝐭𝐢𝐟𝐢𝐪𝐮𝐞𝐬": "Relations",
    " 𝐀𝐧𝐚𝐥𝐲𝐬𝐞 𝐝𝐞𝐬 𝐭𝐞𝐧𝐝𝐚𝐧𝐜𝐞𝐬": "Tendances"
}

# Affichage du menu dans la barre latérale
choice = st.sidebar.radio("", list(pages.keys()))

# Routage vers les modules
if pages[choice] == "Overview":
    overview_tab.main()
elif pages[choice] == "Recherche":
    search_tab.main()
elif pages[choice] == "Clusters":
    cluster_tab.main()
elif pages[choice] == "Relations":
    relations_tab.main()
elif pages[choice] == "Tendances":
    trends_tab.main()
