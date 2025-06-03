import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from utils.db_utils import connect_db

N_CLUSTERS = 6  # Nombre de clusters thématiques

def fetch_concepts():
    conn = connect_db()
    query = '''
        SELECT article_id, entity
        FROM named_entities
        WHERE label = 'CONCEPT';
    '''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def build_corpus(df):
    # Regrouper les concepts par article
    grouped = df.groupby('article_id')['entity'].apply(lambda x: ' '.join(set(x))).reset_index()
    return grouped

def perform_clustering(corpus_df):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus_df['entity'])

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    clusters = kmeans.fit_predict(X)

    corpus_df['cluster'] = clusters
    return corpus_df[['article_id', 'cluster']]

def save_clusters(cluster_df):
    conn = connect_db()
    cur = conn.cursor()

    # Créer la table si elle n'existe pas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS article_clusters (
            article_id INT PRIMARY KEY,
            cluster INT
        );
    """)

    # Insérer les données
    insert_query = '''
        INSERT INTO article_clusters (article_id, cluster)
        VALUES (%s, %s)
        ON CONFLICT (article_id) DO UPDATE SET cluster = EXCLUDED.cluster;
    '''
    cur.executemany(insert_query, cluster_df.values.tolist())
    conn.commit()
    cur.close()
    conn.close()
    print(f" Clustering terminé : {len(cluster_df)} articles classés.")

if __name__ == "__main__":
    df_concepts = fetch_concepts()
    corpus_df = build_corpus(df_concepts)
    cluster_results = perform_clustering(corpus_df)
    save_clusters(cluster_results)
