import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from neo4j import GraphDatabase
from utils.db_utils import connect_db

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "00000000"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def fetch_data():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT id, title, source, url FROM articles;")
    articles = cur.fetchall()

    cur.execute("SELECT name FROM authors;")
    authors = cur.fetchall()

    cur.execute("""
        SELECT aa.article_id, au.name 
        FROM article_authors aa
        JOIN authors au ON aa.author_id = au.id;
    """)
    article_authors = cur.fetchall()

    cur.execute("SELECT article_id, entity, label FROM named_entities;")
    entities = cur.fetchall()

    cur.close()
    conn.close()
    return articles, authors, article_authors, entities

def generate_coauthor_pairs(article_authors):
    from collections import defaultdict
    coauthor_relations = []
    articles = defaultdict(list)

    for article_id, author_name in article_authors:
        articles[article_id].append(author_name)

    for authors in articles.values():
        authors = sorted(set(authors))
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                coauthor_relations.append((authors[i], authors[j]))
    return coauthor_relations

def insert_data():
    articles, authors, article_authors, entities = fetch_data()

    with driver.session() as session:
        # Insert Articles
        for art in articles:
            session.run("""
                MERGE (a:Article {id: $id})
                SET a.title = $title, a.source = $source, a.url = $url
            """, id=art[0], title=art[1], source=art[2], url=art[3])

        # Insert Authors
        for auth in authors:
            session.run("""
                MERGE (au:Author {name: $name})
            """, name=auth[0])

        # Insert AUTHORED relations
        for aa in article_authors:
            session.run("""
                MATCH (a:Article {id: $article_id})
                MATCH (au:Author {name: $author_name})
                MERGE (au)-[:AUTHORED]->(a)
            """, article_id=aa[0], author_name=aa[1])

        # Insert Entities (Concepts, Results, Institutions)
        for ent in entities:
            label = ent[2].capitalize()
            session.run(f"""
                MERGE (e:{label} {{name: $name}})
            """, name=ent[1])

            session.run(f"""
                MATCH (a:Article {{id: $article_id}})
                MATCH (e:{label} {{name: $name}})
                MERGE (a)-[:MENTIONS]->(e)
            """, article_id=ent[0], name=ent[1])

        # Insert COAUTHOR relations
        coauthor_relations = generate_coauthor_pairs(article_authors)
        for author1, author2 in coauthor_relations:
            session.run("""
                MATCH (a1:Author {name: $author1})
                MATCH (a2:Author {name: $author2})
                MERGE (a1)-[:COAUTHOR]->(a2)
            """, author1=author1, author2=author2)

    print(" Nœuds et relations principales insérés dans Neo4j.")

if __name__ == "__main__":
    insert_data()
