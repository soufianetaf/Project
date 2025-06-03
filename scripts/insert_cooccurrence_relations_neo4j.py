import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from neo4j import GraphDatabase
from utils.db_utils import connect_db

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "00000000"

BATCH_SIZE = 1000

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_indexes():
    with driver.session() as session:
        session.run("CREATE INDEX IF NOT EXISTS FOR (c:Concept) ON (c.name);")
        session.run("CREATE INDEX IF NOT EXISTS FOR (r:Result) ON (r.name);")
    print(" Index créés dans Neo4j.")

def fetch_filtered_relations():
    conn = connect_db()
    cur = conn.cursor()

    query = """
        SELECT r.entity1, r.entity2
        FROM relations r
        JOIN (
            SELECT entity, COUNT(DISTINCT article_id) as freq
            FROM named_entities
            WHERE label = 'CONCEPT'
            GROUP BY entity
        ) freq1 ON r.entity1 = freq1.entity
        JOIN (
            SELECT entity, COUNT(DISTINCT article_id) as freq
            FROM named_entities
            WHERE label = 'CONCEPT'
            GROUP BY entity
        ) freq2 ON r.entity2 = freq2.entity
        WHERE freq1.freq >= 3 AND freq2.freq >= 3
        AND r.relation_type = 'COOCCURRENCE';
    """

    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    print(f"🔹 {len(data)} relations filtrées prêtes à être insérées.")
    return data

def insert_relations_batch(relations):
    with driver.session() as session:
        for i in range(0, len(relations), BATCH_SIZE):
            batch = relations[i:i+BATCH_SIZE]
            tx = session.begin_transaction()
            for entity1, entity2 in batch:
                if entity1 == entity2:
                    continue
                tx.run("""
                    MATCH (e1 {name: $entity1})
                    MATCH (e2 {name: $entity2})
                    MERGE (e1)-[:COOCCURS_WITH]->(e2)
                """, entity1=entity1, entity2=entity2)
            tx.commit()
            print(f" Batch {i//BATCH_SIZE + 1} inséré.")

if __name__ == "__main__":
    create_indexes()
    relations = fetch_filtered_relations()
    insert_relations_batch(relations)
    print(" Insertion des relations COOCCURRENCE terminée avec filtrage intelligent.")
