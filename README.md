# Projet SD - Outil d'Exploration et Visualisation des Articles Scientifiques

## Description
Le projet consiste à développer un outil permettant l'extraction automatisée des connaissances à partir des publications scientifiques. L'objectif est de structurer ces connaissances et de les visualiser de manière intuitive. Ce projet s'inscrit dans un contexte où la croissance exponentielle des publications scientifiques rend la gestion des données et leur exploration plus complexes.

### Objectifs du projet
- Extraction des données depuis des bases de données comme **arXiv**.
- Prétraitement linguistique des articles scientifiques pour en extraire des entités et des relations importantes.
- Clustering thématique des publications pour identifier les grands axes de recherche.
- Visualisation interactive des données à travers un tableau de bord web.

## Fonctionnalités
- **Collecte de données**: Extraction de 20 000 articles scientifiques d'arXiv avec des métadonnées telles que le titre, le résumé, les auteurs, la date de publication, etc.
- **Prétraitement linguistique**: Utilisation de la reconnaissance d'entités nommées (NER) pour extraire les auteurs, institutions, concepts et résultats expérimentaux.
- **Clustering thématique**: Application de l'algorithme KMeans pour regrouper les publications selon leurs thématiques.
- **Stockage des données**: Utilisation de bases de données relationnelles (PostgreSQL) et orientées graphe (Neo4j).
- **Visualisation interactive**: Développement d'une interface utilisateur web pour la visualisation des résultats.

## Installation

### Prérequis
Assurez-vous d'avoir installé les outils suivants :
- **Python 3.x**
- **PostgreSQL**
- **Neo4j**
- **Bibliothèques Python**: Vous pouvez installer les dépendances via `pip` :

```bash
pip install -r requirements.txt
