import os
import json
import time
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# 1. Load environment variables
load_dotenv()

def normalize_concepts():
    input_file = "data/master_graph_data.json"
    output_file = "data/normalized_graph_data.json"
    
    # 2. Load the raw extracted data
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 3. Extract unique concepts (ignoring case and whitespace)
    print("Extracting unique concepts from the dataset...")
    raw_concepts = set()
    for triplet in data:
        raw_concepts.add(triplet['intervention'].lower().strip())
        raw_concepts.add(triplet['outcome'].lower().strip())
    
    unique_concepts = list(raw_concepts)
    print(f"Found {len(unique_concepts)} unique raw concepts to process.")

    # 4. Generate Text Embeddings locally
    # all-MiniLM-L6-v2 is the industry standard for fast, accurate semantic matching
    print("\nLoading embedding model (this may take a minute to download on the first run)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating vector embeddings...")
    embeddings = model.encode(unique_concepts)

    # 5. Initialize Pinecone Database
    print("\nConnecting to Pinecone...")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "digital-detox-knowledge-graph"

    # Check if index exists; if not, create a serverless index
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Creating new Pinecone index: '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=384, # The exact output dimension of the MiniLM model
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        # Give Pinecone a few seconds to boot up the new index
        time.sleep(10) 

    index = pc.Index(index_name)

    # 6. Upsert Vectors to Pinecone
    print("Uploading vectors to Pinecone database...")
    vectors_to_upsert = []
    for i, concept in enumerate(unique_concepts):
        vectors_to_upsert.append({
            "id": str(i),
            "values": embeddings[i].tolist(),
            "metadata": {"text": concept}
        })
    
    # Batch upsert in chunks of 100
    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        index.upsert(vectors=vectors_to_upsert[i:i+batch_size])
    
    # 7. Query Database for Semantic Duplicates & Create Normalization Map
    print("\nCalculating semantic similarity and normalizing concepts...")
    canonical_map = {}
    processed_ids = set()

    for i, concept in enumerate(unique_concepts):
        if str(i) in processed_ids:
            continue
            
        # Query Pinecone for vectors highly similar to the current concept
        query_res = index.query(
            vector=embeddings[i].tolist(),
            top_k=10,
            include_metadata=True
        )
        
        # Group concepts with a similarity score of 85% or higher
        cluster = []
        for match in query_res['matches']:
            if match['score'] >= 0.85:
                cluster.append(match)
                processed_ids.add(match['id'])
        
        if cluster:
            # Get the text of all matching concepts
            cluster_texts = [m['metadata']['text'] for m in cluster]
            
            # Choose the shortest string in the cluster as the clean "canonical" name
            # e.g., mapping "reduction in smartphone usage" to "smartphone reduction"
            canonical_name = min(cluster_texts, key=len).title()
            
            # Map every variation to this single canonical name
            for text in cluster_texts:
                canonical_map[text] = canonical_name

    # 8. Apply Normalization Map to the Dataset
    print("\nApplying unified entities to the master dataset...")
    normalized_data = []
    for triplet in data:
        orig_intervention = triplet['intervention'].lower().strip()
        orig_outcome = triplet['outcome'].lower().strip()
        
        normalized_triplet = {
            "intervention": canonical_map.get(orig_intervention, triplet['intervention'].title()),
            "relationship": triplet['relationship'].lower().strip(),
            "outcome": canonical_map.get(orig_outcome, triplet['outcome'].title()),
            "source_paper": triplet['source_paper']
        }
        normalized_data.append(normalized_triplet)
        
    # 9. Save Final Normalized Data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized_data, f, indent=4)
        
    print("="*50)
    print(f"Normalization complete!")
    print(f"Reduced {len(unique_concepts)} fragmented concepts down to {len(set(canonical_map.values()))} unified entities.")
    print(f"Saved cleanly to {output_file}")
    print("="*50)

if __name__ == "__main__":
    normalize_concepts()