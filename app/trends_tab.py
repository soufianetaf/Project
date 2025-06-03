
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# Connexion à la base de données
def connect_db():
    return psycopg2.connect(
        host="localhost",
        dbname="db_articles",
        user="postgres",
        password="0000"
    )

@st.cache_data
def load_concepts():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT entity FROM named_entities WHERE label = 'CONCEPT';")
    concepts = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return sorted(concepts)

@st.cache_data
def get_concept_trend(concept):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT EXTRACT(YEAR FROM a.publication_date) AS year, COUNT(*) 
        FROM named_entities ne
        JOIN articles a ON ne.article_id = a.id
        WHERE ne.label = 'CONCEPT' AND ne.entity = %s AND a.publication_date IS NOT NULL
        GROUP BY year
        ORDER BY year;
    """, (concept,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(data, columns=["Année", "Occurrences"])

def plot_trend(df, concept):
    fig = px.line(
        df,
        x="Année",
        y="Occurrences",
        markers=True,
        title=f" Évolution du concept : {concept}",
        labels={"Année": "Année", "Occurrences": "Occurrences"}
    )
    fig.update_traces(hovertemplate='Année: %{x}<br>Occurrences: %{y}')
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.markdown("<h1><i class='fas fa-chart-line'></i> Analyse des tendances dans le temps</h1>", unsafe_allow_html=True)

    #st.title("📈 Analyse des tendances dans le temps")

    concepts = load_concepts()
    st.markdown("<label><i class='fas fa-search'></i> Sélectionnez un concept à analyser :</label>", unsafe_allow_html=True)
    selected_concept = st.selectbox("", concepts)


    if selected_concept:
        trend_df = get_concept_trend(selected_concept)
        if trend_df.empty:
            st.warning("Aucune donnée disponible pour ce concept.")
        else:
            st.success(f"{len(trend_df)} année(s) trouvée(s) pour ce concept.")
            plot_trend(trend_df, selected_concept)

if __name__ == "__main__":
    main()
