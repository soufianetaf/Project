
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import xml.etree.ElementTree as ET
from utils.db_utils import connect_db

ARXIV_API_URL = "http://export.arxiv.org/api/query"

categories = ['cs.AI', 'cs.LG', 'cs.CR', 'cs.NI', 'cs.CV', 'cs.SE', 'cs.RO']

def fetch_arxiv_articles(category, start=0, max_results=3000, batch_size=100):
    articles = []
    authors_links = []

    for i in range(start, start + max_results, batch_size):
        params = {
            "search_query": f"cat:{category}",
            "start": i,
            "max_results": batch_size
        }
        response = requests.get(ARXIV_API_URL, params=params)

        if response.status_code != 200:
            print(f" Erreur HTTP : {response.status_code} pour batch {i} dans {category}")
            continue

        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            print(f" Erreur de parsing XML au batch {i} dans {category}")
            continue

        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        
        for entry in entries:
            try:
                external_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                abstract = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                pub_date = entry.find('atom:published', ns).text
                url = entry.find('atom:id', ns).text

                articles.append(('arXiv', external_id, title, abstract, pub_date, url))

                authors = entry.findall('atom:author', ns)
                for author in authors:
                    name = author.find('atom:name', ns).text.strip()
                    authors_links.append((external_id, name))

            except Exception as e:
                print(f" Erreur sur une entrée : {e}")
                continue
        
        print(f" {category} : Batch {i} à {i + batch_size}")

    return articles, authors_links

def insert_articles_and_authors(articles, authors_links):
    conn = connect_db()
    cur = conn.cursor()

    insert_article_query = """
INSERT INTO articles (source, external_id, title, abstract, publication_date, url)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING;
"""
    cur.executemany(insert_article_query, articles)
    print(f" {len(articles)} articles insérés.")

    for ext_id, author_name in authors_links:
        cur.execute("""
INSERT INTO authors (name)
VALUES (%s)
ON CONFLICT (name) DO NOTHING;
""", (author_name,))
        
        cur.execute("SELECT id FROM articles WHERE external_id = %s AND source = 'arXiv';", (ext_id,))
        article_res = cur.fetchone()
        if article_res:
            article_id = article_res[0]
            cur.execute("SELECT id FROM authors WHERE name = %s;", (author_name,))
            author_res = cur.fetchone()
            if author_res:
                author_id = author_res[0]
                cur.execute("""
INSERT INTO article_authors (article_id, author_id)
VALUES (%s, %s)
ON CONFLICT DO NOTHING;
""", (article_id, author_id))

    conn.commit()
    cur.close()
    conn.close()
    print(f" Auteurs et liaisons insérés.")

if __name__ == "__main__":
    total_articles = 0
    for cat in categories:
        articles, authors_links = fetch_arxiv_articles(category=cat)
        insert_articles_and_authors(articles, authors_links)
        total_articles += len(articles)

    print(f" Extraction terminée. Total articles récupérés (avant dédoublonnage) : {total_articles}")
