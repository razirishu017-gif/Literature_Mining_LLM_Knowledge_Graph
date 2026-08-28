import json
import networkx as nx

def analyze_graph():
    input_file = "data/normalized_graph_data.json"
    
    print("Loading normalized dataset...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Initialize a Directed Graph
    G = nx.DiGraph()

    # 2. Populate the Graph with Nodes and Edges
    print("Building the Knowledge Graph...")
    for triplet in data:
        intervention = triplet['intervention']
        outcome = triplet['outcome']
        relationship = triplet['relationship']
        
        # Adding an edge automatically creates the nodes if they don't exist
        G.add_edge(intervention, outcome, label=relationship)

    # 3. Compute Basic Network Statistics
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = nx.density(G)

    print("\n" + "="*50)
    print("KNOWLEDGE GRAPH STATISTICS")
    print("="*50)
    print(f"Total Concepts (Nodes): {num_nodes}")
    print(f"Total Relationships (Edges): {num_edges}")
    print(f"Network Density: {density:.4f}")

    # 4. Calculate Degree Centrality (Most Connected Concepts)
    # This identifies the most frequently studied interventions and outcomes
    degree_dict = nx.degree_centrality(G)
    sorted_degree = sorted(degree_dict.items(), key=lambda item: item[1], reverse=True)

    print("\n--- Top 10 Most Influential Concepts (Degree Centrality) ---")
    for concept, score in sorted_degree[:10]:
        print(f"- {concept} (Score: {score:.4f})")

    # 5. Calculate Betweenness Centrality (Bridging Concepts)
    # This identifies concepts that connect different areas of research together
    betweenness_dict = nx.betweenness_centrality(G)
    sorted_betweenness = sorted(betweenness_dict.items(), key=lambda item: item[1], reverse=True)

    print("\n--- Top 10 Bridging Concepts (Betweenness Centrality) ---")
    for concept, score in sorted_betweenness[:10]:
        print(f"- {concept} (Score: {score:.4f})")
        
    print("="*50 + "\n")

if __name__ == "__main__":
    analyze_graph()