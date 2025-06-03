import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import spacy
from utils.db_utils import connect_db

# Charger SciSpacy sans le NER (juste pour le prétraitement)
nlp = spacy.load("en_core_sci_sm", disable=["ner"])

def preprocess_sentence(sentence):
    doc = nlp(sentence)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(tokens)

def fetch_abstracts():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, abstract FROM articles WHERE abstract IS NOT NULL;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def save_sentences(sentences):
    conn = connect_db()
    cur = conn.cursor()
    insert_query = """
        INSERT INTO preprocessed_sentences (article_id, sentence_number, clean_sentence)
        VALUES (%s, %s, %s);
    """
    cur.executemany(insert_query, sentences)
    conn.commit()
    cur.close()
    conn.close()
    print(f" {len(sentences)} phrases prétraitées insérées.")

if __name__ == "__main__":
    abstracts = fetch_abstracts()
    results = []

    print(f"🔹 Prétraitement avec segmentation sur {len(abstracts)} abstracts...")

    for article_id, abstract in abstracts:
        doc = nlp(abstract)
        for idx, sent in enumerate(doc.sents, start=1):
            clean_sent = preprocess_sentence(sent.text)
            if clean_sent:  # On évite d'enregistrer des phrases vides
                results.append((article_id, idx, clean_sent))

    save_sentences(results)
