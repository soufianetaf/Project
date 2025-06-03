import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import spacy
from utils.db_utils import connect_db

# Charger SciSpacy
nlp = spacy.load("en_core_sci_sm")

# Listes de détection
INSTITUTION_KEYWORDS = ["university", "institute", "college", "school", "laboratory", "centre", "center"]
RESULT_KEYWORDS = ["achieve", "accuracy", "result", "improve", "increase", "%"]
GENERIC_WORDS = ["result", "method", "study", "paper", "approach", "analysis", "data"]

# Limite pour éviter de capturer des phrases entières
MAX_ENTITY_WORDS = 6

def is_valid_entity(ent_text):
    text = ent_text.lower()
    words = text.split()
    # Filtrer :
    if len(words) > MAX_ENTITY_WORDS:
        return False  # Trop long pour être une entité pertinente
    if len(text) < 3:
        return False  # Trop court
    if text in GENERIC_WORDS:
        return False  # Mot générique inutile
    return True

def is_result(ent_text):
    text = ent_text.lower()
    words = text.split()
    if any(char.isdigit() for char in text) or "%" in text:
        return True
    if len(words) >= 2 and any(keyword in text for keyword in RESULT_KEYWORDS):
        return True
    return False

def classify_entity(ent_text):
    text = ent_text.lower()
    if any(keyword in text for keyword in INSTITUTION_KEYWORDS):
        return "INSTITUTION"
    elif is_result(text):
        return "RESULT"
    else:
        return "CONCEPT"

def fetch_sentences():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT article_id, clean_sentence FROM preprocessed_sentences;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def insert_named_entities(entities):
    conn = connect_db()
    cur = conn.cursor()
    insert_query = '''
        INSERT INTO named_entities (article_id, entity, label)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
    '''
    cur.executemany(insert_query, entities)
    conn.commit()
    cur.close()
    conn.close()
    print(f" {len(entities)} entités insérées dans named_entities.")

if __name__ == "__main__":
    sentences = fetch_sentences()
    all_entities = []

    print(f" Extraction optimisée des entités sur {len(sentences)} phrases...")

    for article_id, sentence in sentences:
        doc = nlp(sentence)
        for ent in doc.ents:
            if not is_valid_entity(ent.text):
                continue
            label = classify_entity(ent.text)
            all_entities.append((article_id, ent.text.strip(), label))

    insert_named_entities(all_entities)
