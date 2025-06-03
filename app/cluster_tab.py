import streamlit as st
import psycopg2
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# Connexion PostgreSQL
def connect_db():
    return psycopg2.connect(
        host="localhost",
        dbname="db_articles",
        user="postgres",
        password="0000"
    )

@st.cache_data
def get_clusters():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT cluster FROM article_clusters ORDER BY cluster;")
    clusters = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return clusters

@st.cache_data
def get_articles_by_cluster(cluster_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.title, a.url
        FROM articles a
        JOIN article_clusters ac ON a.id = ac.article_id
        WHERE ac.cluster = %s;
    """, (cluster_id,))
    articles = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(articles, columns=["ID", "Titre", "URL"])

@st.cache_data
def get_concepts_by_cluster(cluster_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT ne.entity
        FROM named_entities ne
        JOIN article_clusters ac ON ne.article_id = ac.article_id
        WHERE ne.label = 'CONCEPT' AND ac.cluster = %s;
    """, (cluster_id,))
    concepts = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return concepts

def plot_wordcloud(concepts):
    word_freq = Counter(concepts)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

def main():
    # Ajout Font Awesome
    st.markdown("""
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <h1><i class="fas fa-layer-group"></i> Thématiques principales par cluster</h1>
        <hr>
    """, unsafe_allow_html=True)

    clusters = get_clusters()
    st.markdown("<b><i class='fas fa-diagram-project'></i> Choisissez un cluster :</b>", unsafe_allow_html=True)
    cluster_id = st.selectbox(" ", clusters, label_visibility="collapsed")

    if cluster_id is not None:
        st.markdown("<h3><i class='fas fa-tags'></i> Concepts fréquents</h3>", unsafe_allow_html=True)
        concepts = get_concepts_by_cluster(cluster_id)
        if not concepts:
            st.info("Aucun concept trouvé pour ce cluster.")
        else:
            top_concepts = Counter(concepts).most_common(10)
            for concept, freq in top_concepts:
                st.write(f"- {concept} ({freq})")

            st.markdown("<h3><i class='fas fa-cloud'></i> Nuage de mots des concepts</h3>", unsafe_allow_html=True)
            plot_wordcloud(concepts)

        st.markdown("<h3><i class='fas fa-file-alt'></i> Articles de ce cluster</h3>", unsafe_allow_html=True)
        with st.expander(" Voir la liste des articles de ce cluster", expanded=False):
            for _, row in get_articles_by_cluster(cluster_id).iterrows():
                st.markdown(f"- [{row['Titre']}]({row['URL']})", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
