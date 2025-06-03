import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_utils import connect_db

def fetch_article_authors():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, array_agg(au.name)
        FROM articles a
        JOIN article_authors aa ON a.id = aa.article_id
        JOIN authors au ON aa.author_id = au.id
        GROUP BY a.id;
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def generate_coauthor_pairs(article_id, authors_list):
    pairs = []
    unique_authors = sorted(set(authors_list))
    for i in range(len(unique_authors)):
        for j in range(i + 1, len(unique_authors)):
            pairs.append((article_id, unique_authors[i], unique_authors[j], "COAUTHOR"))
    return pairs

def insert_relations(relations):
    conn = connect_db()
    cur = conn.cursor()
    insert_query = """
        INSERT INTO relations (article_id, entity1, entity2, relation_type)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """
    cur.executemany(insert_query, relations)
    conn.commit()
    cur.close()
    conn.close()
    print(f" {len(relations)} relations COAUTHOR insérées.")

if __name__ == "__main__":
    articles_authors = fetch_article_authors()
    all_relations = []

    for article_id, authors in articles_authors:
        if len(authors) > 1:
            pairs = generate_coauthor_pairs(article_id, authors)
            all_relations.extend(pairs)

    insert_relations(all_relations)
