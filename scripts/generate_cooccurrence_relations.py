import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_utils import connect_db

def fetch_entities():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT article_id, entity, label
        FROM named_entities
        WHERE label IN ('CONCEPT', 'RESULT');
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def generate_cooccurrence_pairs(entities_by_article):
    relations = []
    for article_id, entities in entities_by_article.items():
        concepts = [e for e in entities if e[1] == 'CONCEPT']
        results = [e for e in entities if e[1] == 'RESULT']

        # CONCEPT - CONCEPT
        concept_texts = sorted(set([c[0] for c in concepts]))
        for i in range(len(concept_texts)):
            for j in range(i + 1, len(concept_texts)):
                relations.append((article_id, concept_texts[i], concept_texts[j], "COOCCURRENCE"))

        # CONCEPT - RESULT
        for concept in concept_texts:
            for result in set([r[0] for r in results]):
                relations.append((article_id, concept, result, "COOCCURRENCE"))

    return relations

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
    print(f" {len(relations)} relations COOCCURRENCE insérées.")

if __name__ == "__main__":
    data = fetch_entities()

    # Organiser les entités par article
    entities_by_article = {}
    for article_id, entity, label in data:
        entities_by_article.setdefault(article_id, []).append((entity, label))

    relations = generate_cooccurrence_pairs(entities_by_article)
    insert_relations(relations)
