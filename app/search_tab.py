import streamlit as st
import psycopg2
import pandas as pd

# Connexion à la base PostgreSQL
def connect_db():
    return psycopg2.connect(
        host="localhost",
        dbname="db_articles",
        user="postgres",
        password="0000"
    )

# Fonction de recherche filtrée
def search_articles(keyword=None, author=None, institution=None):
    conn = connect_db()
    cur = conn.cursor()

    query = '''
        SELECT a.id, a.title, a.source, a.url
        FROM articles a
        LEFT JOIN article_authors aa ON a.id = aa.article_id
        LEFT JOIN authors au ON aa.author_id = au.id
        LEFT JOIN named_entities ne ON a.id = ne.article_id AND ne.label = 'INSTITUTION'
        WHERE 1=1
    '''
    params = []

    if keyword:
        query += " AND (LOWER(a.title) LIKE %s OR LOWER(a.abstract) LIKE %s)"
        params.extend([f"%{keyword.lower()}%", f"%{keyword.lower()}%"])

    if author:
        query += " AND LOWER(au.name) LIKE %s"
        params.append(f"%{author.lower()}%")

    if institution:
        query += " AND LOWER(ne.entity) LIKE %s"
        params.append(f"%{institution.lower()}%")

    query += " GROUP BY a.id ORDER BY a.id DESC LIMIT 100;"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return pd.DataFrame(rows, columns=["ID", "Titre", "Source", "URL"])

# Interface Streamlit
def main():
    st.markdown("""
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <h1><i class="fas fa-search"></i> Recherche avancée de publications</h1>
        <hr>
    """, unsafe_allow_html=True)

    st.markdown("<b><i class='fas fa-key'></i> Mot-clé (titre ou résumé)</b>", unsafe_allow_html=True)
    keyword = st.text_input(" ", label_visibility="collapsed")

    st.markdown("<b><i class='fas fa-user'></i> Nom d’auteur</b>", unsafe_allow_html=True)
    author = st.text_input("  ", label_visibility="collapsed")

    st.markdown("<b><i class='fas fa-building'></i> Institution</b>", unsafe_allow_html=True)
    institution = st.text_input("   ", label_visibility="collapsed")

    if st.button(" Rechercher"):
        results = search_articles(keyword, author, institution)
        if results.empty:
            st.warning("Aucun article trouvé avec ces critères.")
        else:
            st.success(f"{len(results)} article(s) trouvé(s).")
            st.dataframe(results, use_container_width=True)

if __name__ == "__main__":
    main()
