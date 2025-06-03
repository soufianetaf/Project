import streamlit as st
from pyvis.network import Network
from neo4j import GraphDatabase
import streamlit.components.v1 as components

# Connexion Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "00000000"

@st.cache_resource
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def fetch_nodes_and_edges(relation_type, skip, limit):
    driver = get_driver()
    with driver.session() as session:
        if relation_type == "COAUTHOR":
            query = f'''
                MATCH (a1:Author)-[:COAUTHOR]->(a2:Author)
                RETURN a1.name AS source, a2.name AS target SKIP {skip} LIMIT {limit}
            '''
        elif relation_type == "COOCCURRENCE":
            query = f'''
                MATCH (e1)-[:COOCCURS_WITH]->(e2)
                RETURN e1.name AS source, e2.name AS target SKIP {skip} LIMIT {limit}
            '''
        elif relation_type == "AUTHORED":
            query = f'''
                MATCH (au:Author)-[:AUTHORED]->(a:Article)
                RETURN au.name AS source, a.title AS target SKIP {skip} LIMIT {limit}
            '''
        elif relation_type == "MENTIONS":
            query = f'''
                MATCH (a:Article)-[:MENTIONS]->(e)
                RETURN a.title AS source, e.name AS target SKIP {skip} LIMIT {limit}
            '''
        else:
            return [], []

        result = session.run(query)
        edges = [(record["source"], record["target"]) for record in result]
        nodes = set([n for edge in edges for n in edge])

        # Récupérer les labels des noeuds pour la couleur et l’icône
        labels_query = '''
            MATCH (n) WHERE n.name IN $nodes OR n.title IN $nodes
            RETURN n.name AS name, labels(n) AS labels
        '''
        nodes_with_labels = {}
        label_result = session.run(labels_query, nodes=list(nodes))
        for record in label_result:
            name = record["name"]
            labels = record["labels"]
            nodes_with_labels[name] = labels

        return list(nodes), edges, nodes_with_labels

def draw_graph(nodes, edges, nodes_with_labels, title):
    net = Network(height="600px", width="100%", notebook=False)
    net.barnes_hut()

    # Couleurs et icônes selon le label
    label_colors = {
        "Article": "#1f77b4",       # bleu
        "Author": "#ff7f0e",        # orange
        "Concept": "#2ca02c",       # vert
        "Institution": "#d62728",   # rouge
        "Result": "#9467bd",        # violet
    }

    label_icons = {
        "Article": "📄",
        "Author": "👤",
        "Concept": "💡",
        "Institution": "🏢",
        "Result": "📊",
    }

    # Ajout des noeuds avec couleur et icône dans le label
    for node in nodes:
        labels = nodes_with_labels.get(node, [])
        color = "#999999"  # gris par défaut si label non trouvé
        icon = ""
        for label in label_colors.keys():
            if label in labels:
                color = label_colors[label]
                icon = label_icons[label]
                break
        net.add_node(node, label=f"{icon} {node}", color=color, title=node)

    for source, target in edges:
        net.add_edge(source, target)

    net.set_options("""
    var options = {
      "nodes": {
        "shape": "dot",
        "size": 18,
        "font": {
          "size": 20
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -20000,
          "springLength": 100
        },
        "minVelocity": 0.75
      }
    }
    """)

    net.save_graph("graph.html")
    HtmlFile = open("graph.html", "r", encoding="utf-8")
    components.html(HtmlFile.read(), height=650)

def main():
    # Charger CSS FontAwesome pour icônes HTML (si besoin d’autres icônes plus tard)
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    """, unsafe_allow_html=True)

    st.markdown("<h1><i class='fas fa-search'></i> Cartographie des relations scientifiques</h1>", unsafe_allow_html=True)

    st.markdown("<h3><i class='fas fa-project-diagram'></i> Type de relations :</h3>", unsafe_allow_html=True)
    relation_type = st.selectbox("", ["COAUTHOR", "COOCCURRENCE", "AUTHORED", "MENTIONS"])

    st.markdown("<h3><i class='fas fa-forward'></i> Sauter combien de relations ?</h3>", unsafe_allow_html=True)
    skip = st.number_input("", min_value=0, max_value=10000000, value=0, step=100)

    st.markdown("<h3><i class='fas fa-list-ol'></i> Nombre de relations à afficher :</h3>", unsafe_allow_html=True)
    limit = st.number_input("", min_value=1, max_value=1000000, value=200, step=100)

    nodes, edges, nodes_with_labels = fetch_nodes_and_edges(relation_type, skip, limit)

    if not edges:
        st.warning("Aucune relation trouvée.")
    else:
        st.subheader(f"Graphe des relations : {relation_type} (affiche {len(edges)} liens)")
        draw_graph(nodes, edges, nodes_with_labels, f"Relations {relation_type}")

if __name__ == "__main__":
    main()
