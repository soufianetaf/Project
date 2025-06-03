import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

def connect_db():
    return psycopg2.connect(
        host="localhost",
        dbname="db_articles",
        user="postgres",
        password="0000",
        port="5432"
    )

def get_kpi_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM articles")
    nb_articles = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT id) FROM authors")
    nb_auteurs = cursor.fetchone()[0]

    nb_relations = 5020069  # Valeur fixe, adapte si besoin

    cursor.execute("SELECT COUNT(DISTINCT cluster) FROM article_clusters")
    nb_clusters = cursor.fetchone()[0]

    cursor.close()
    return nb_articles, nb_auteurs, nb_relations, nb_clusters

def get_publications_by_year(conn):
    query = """
        SELECT
            EXTRACT(YEAR FROM publication_date) AS year,
            COUNT(*) AS total
        FROM articles
        GROUP BY year
        ORDER BY year;
    """
    return pd.read_sql_query(query, conn)

def get_authors_by_year(conn):
    query = """
        SELECT
            EXTRACT(YEAR FROM publication_date) AS year,
            COUNT(DISTINCT pa.author_id) AS nb_authors
        FROM articles a
        JOIN article_authors pa ON a.id = pa.article_id
        GROUP BY year
        ORDER BY year;
    """
    return pd.read_sql_query(query, conn)

def get_publications_by_month(conn):
    query = """
        SELECT
            EXTRACT(MONTH FROM publication_date) AS month,
            COUNT(*) AS total
        FROM articles
        GROUP BY month
        ORDER BY month;
    """
    return pd.read_sql_query(query, conn)

def get_top_authors(conn):
    query = """
        SELECT a.name, COUNT(pa.article_id) AS total
        FROM authors a
        JOIN article_authors pa ON a.id = pa.author_id
        GROUP BY a.name
        ORDER BY total DESC
        LIMIT 10
    """
    return pd.read_sql_query(query, conn)

def get_cluster_distribution(conn):
    query = """
        SELECT
            cluster AS cluster_name,
            COUNT(article_id) AS total
        FROM article_clusters
        GROUP BY cluster
        ORDER BY total DESC;
    """
    return pd.read_sql_query(query, conn)

def main():
    st.markdown("###  Vue d'ensemble des données scientifiques")

    # CSS style Power BI-like pour les KPI cards + fontawesome icons
    st.markdown(
        """
        <link
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
          rel="stylesheet"
        />
        <style>
        .kpi-container {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: nowrap;
        }
        .kpi-card {
            flex: 1 1 200px;
            min-width: 220px;
            background-color: #f9fafb;
            border: 2px solid #4a90e2;
            border-radius: 12px;
            padding: 1.5rem 1rem;
            text-align: center;
            box-shadow: 0 4px 8px rgba(74,144,226,0.15);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: transform 0.2s ease-in-out;
            cursor: default;
        }
        .kpi-card:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 14px rgba(74,144,226,0.3);
        }
        .kpi-icon {
            font-size: 2.8rem;
            color: #4a90e2;
            margin-bottom: 0.3rem;
        }
        .kpi-value {
            font-size: 2.7rem;
            font-weight: 700;
            color: #2c3e50;
            margin-top: 0.3rem;
            margin-bottom: 0.3rem;
        }
        .kpi-label {
            font-size: 1.1rem;
            font-weight: 600;
            color: #4a90e2;
        }
        .chart-container {
            margin-bottom: 3rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    conn = connect_db()
    nb_articles, nb_auteurs, nb_relations, nb_clusters = get_kpi_data(conn)

    # Affichage des KPI avec icônes FontAwesome
    st.markdown(
        f"""
        <div class="kpi-container">
            <div class="kpi-card" title="Nombre total d'articles">
                <div class="kpi-icon"><i class="fas fa-file-alt"></i></div>
                <div class="kpi-label">Articles</div>
                <div class="kpi-value">{nb_articles:,}</div>
            </div>
            <div class="kpi-card" title="Nombre total d'auteurs">
                <div class="kpi-icon"><i class="fas fa-user"></i></div>
                <div class="kpi-label">Auteurs</div>
                <div class="kpi-value">{nb_auteurs:,}</div>
            </div>
            <div class="kpi-card" title="Nombre total de relations">
                <div class="kpi-icon"><i class="fas fa-link"></i></div>
                <div class="kpi-label">Relations</div>
                <div class="kpi-value">{nb_relations:,}</div>
            </div>
            <div class="kpi-card" title="Nombre total de clusters">
                <div class="kpi-icon"><i class="fas fa-brain"></i></div>
                <div class="kpi-label">Clusters</div>
                <div class="kpi-value">{nb_clusters:,}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Graphiques avec thème épuré Plotly + couleurs customisées

    # Publications par année
    df_year = get_publications_by_year(conn)
    fig_year = px.bar(
        df_year, x="year", y="total",
        title="Nombre de publications par année",
        labels={"year": "Année", "total": "Nombre de publications"},
        template="plotly_white",
        color_discrete_sequence=["#4a90e2"]
    )
    fig_year.update_layout(margin=dict(t=40, b=20))
    st.plotly_chart(fig_year, use_container_width=True)

    # Évolution du nombre d'auteurs par année
    df_authors_year = get_authors_by_year(conn)
    fig_authors_year = px.line(
        df_authors_year, x="year", y="nb_authors",
        title="Évolution du nombre d'auteurs par année",
        labels={"year": "Année", "nb_authors": "Nombre d'auteurs"},
        template="plotly_white",
        line_shape='spline',
        color_discrete_sequence=["#e94e77"]
    )
    fig_authors_year.update_traces(mode='lines+markers')
    fig_authors_year.update_layout(margin=dict(t=40, b=20))
    st.plotly_chart(fig_authors_year, use_container_width=True)

    # Répartition des articles par mois (moyenne sur toutes les années)
    df_month = get_publications_by_month(conn)
    # Remplacer le numéro du mois par le nom du mois
    mois = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
    df_month["month_name"] = df_month["month"].apply(lambda x: mois[int(x)-1])
    fig_month = px.bar(
        df_month, x="month_name", y="total",
        title="Répartition moyenne des publications par mois",
        labels={"month_name": "Mois", "total": "Nombre moyen de publications"},
        template="plotly_white",
        color_discrete_sequence=["#f39c12"]
    )
    fig_month.update_layout(margin=dict(t=40, b=20))
    st.plotly_chart(fig_month, use_container_width=True)

    # Top auteurs
    df_authors = get_top_authors(conn)
    fig_authors = px.bar(
        df_authors, x="name", y="total",
        title="Top 10 des auteurs les plus prolifiques",
        labels={"name": "Auteur", "total": "Nombre d'articles"},
        template="plotly_white",
        color_discrete_sequence=["#27ae60"]
    )
    fig_authors.update_layout(margin=dict(t=40, b=20))
    st.plotly_chart(fig_authors, use_container_width=True)

    # Répartition des clusters
    df_clusters = get_cluster_distribution(conn)
    fig_cluster = px.pie(
        df_clusters, names="cluster_name", values="total",
        title="Répartition des publications par cluster",
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_cluster.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_cluster, use_container_width=True)

    

    conn.close()

if __name__ == "__main__":
    main()
