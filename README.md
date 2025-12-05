# Football Player Clustering & Analysis Project

This project aims to analyze football player statistics from the '23-'24 season to identify distinct player types, specific playing styles, and performance metrics using various machine learning and data mining techniques.

The workflow is divided into three main stages: **Data Extraction**, **Data Processing**, and **Analysis & Modeling**.


## Installation & Usage

This project uses [`uv`](https://github.com/astral-sh/uv) for dependency management.

### Setup
Install dependencies with:
```bash
uv sync
```

### Running Notebooks
To launch the Jupyter environment:
```bash
uv run jupyter lab
# or
uv run jupyter notebook
```

### Running Scripts
To run the extraction script (example):
```bash
uv run src/data/soccerdata_extraction_extensive.py
```

## 1. Data Extraction

**Script:** [`./src/data/soccerdata_extraction_extensive.py`](src/data/soccerdata_extraction_extensive.py)

This script handles the retrieval of raw data from external sources.
*   **Source:** Uses the `soccerdata` library to scrape data from **FBref**.
*   **Scope:** Covers the "Big 5" European Leagues for the **2023-2024 season**.
*   **Outputs:**
    *   `./data/raw/player_season_stats_23-24.csv`: Main dataset containing extensive player statistics.
    *   `./data/raw/keeper_season_stats_23-24.csv`: Specific statistics for goalkeepers.

## 2. Data Processing & Filtering

**Notebook:** [`./notebooks/data-processing/column_filtering.ipynb`](notebooks/data-processing/column_filtering.ipynb)

This stage cleans and prepares the raw data for analysis.
*   **Input:** Reads the raw data from `data/raw/`.
*   **Process:**
    *   Selects specific columns relevant to player performance (e.g., shooting, passing, defense, possession).
    *   Filters out non-essential metadata.
*   **Output:** Saves the refined dataset to `../../data/interim/player_season_stats_23-24_relevant.csv`, which serves as the foundation for the modeling notebooks.

## 3. Clustering Analysis & Modeling

This section explores different approaches to grouping players and finding insights.

### 3.1 Graph-Based Clustering (Primary Approach)

**Notebooks:**
*   [`./notebooks/data-science/part1_clustering_only.ipynb`](notebooks/data-science/part1_clustering_only.ipynb)
*   [`./notebooks/data-science/graph_clustering_w_visualizations.ipynb`](notebooks/data-science/graph_clustering_w_visualizations.ipynb)

These notebooks implement the core clustering methodology using graph theory.
*   **Methodology:**
    1.  **Preprocessing:** Converts volume stats to per-90 metrics and applies `StandardScaler`.
    2.  **Similarity Graph:** Calculates a **Cosine Similarity** matrix between all players.
    3.  **Graph Construction:** Builds a network graph where edges exist between players with a similarity score > **0.85**.
    4.  **Community Detection:** Uses the graph structure to identify clusters (communities) of similar players.
*   **Key Output:** Generates `../../data/processed/players_w_clusters.csv`, assigning a cluster label to each player. This file is used by downstream analysis notebooks.


### 3.2 Player Recommendation System (LSH)

**Notebook:** [`./notebooks/data-science/lsh.ipynb`](notebooks/data-science/lsh.ipynb)

This notebook implements a scalable similarity search engine.
*   **Technique:** **Locality Sensitive Hashing (LSH)** using P-Stable Distributions for Euclidean Distance.
*   **Purpose:** Efficiently finds the "Nearest Neighbors" for a given player without comparing them to every other player in the dataset.
*   **Application:** Can be used to find "comparable" players for scouting or replacement purposes (e.g., "Who is the most similar player to Bukayo Saka?").

### 3.3 Frequent Pattern Analysis (Apriori)

**Notebook:** [`./notebooks/data-science/Frequency_analysis.ipynb`](notebooks/data-science/Frequency_analysis.ipynb)

This notebook digs deeper into the identified clusters to find statistical rules associated with high performance (specifically goal-scoring).
*   **Input:** Reads `players_w_clusters.csv` and `aggregated_data.csv`.
*   **Methodology:**
    *   **Binary Encoding:** Converts continuous stats into binary values (1 or 0) based on whether a player is in the **90th percentile** for their specific cluster.
    *   **Association Rule Mining:** Uses the **Apriori Algorithm** to find frequent itemsets and rules (e.g., "High xG + High Shot Volume -> High Goals").
*   **Goal:** To identify which specific attributes within a cluster are strongest indicators of goal-scoring success.


### 3.4 DBSCAN Clustering (Alternative Approach)

**Notebook:** [`./notebooks/Clustering/dbscan_test.ipynb`](notebooks/Clustering/dbscan_test.ipynb)

A notebook identifying player clusters based on density rather than graph connectivity.
*   **Methodology:** Uses **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise).
*   **Features:** Includes dimensionality reduction (PCA) for visualizing the resulting clusters.
*   **Comparison:** serves as a validation or alternative perspective to the primary graph-based clustering.
