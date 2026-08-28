import os
import json
import time
import requests
import re
from dotenv import load_dotenv

load_dotenv()

def process_all_papers():
    input_dir = "data/clean_text/"
    output_file = "data/master_graph_data.json"
    master_graph_data = []

    # BROADENED System Prompt to catch both the problem and the solution
    system_prompt = """
    You are an expert clinical data extractor for a Knowledge Graph pipeline.
    Extract evidence-based relationships between digital media usage (e.g., addiction, screen time, passive use) OR digital detox interventions AND their psychological outcomes from the text.

    STRICT RULES:
    1. 'intervention' MUST be a concise concept (e.g., "Social Media Limitation", "Smartphone Addiction", "Passive Browsing").
    2. 'relationship' MUST be a simple directional verb (e.g., "reduces", "increases", "improves", "correlates_with").
    3. 'outcome' MUST be a concise psychological concept (e.g., "Depression", "Loneliness", "Anxiety", "Well-being", "Sleep Quality"). Do NOT place words like 'improved' or 'reduced' in the outcome.

    EXAMPLE OUTPUT FORMAT:
    {
      "triplets": [
        {"intervention": "Social Media Limitation", "relationship": "reduces", "outcome": "Depression"},
        {"intervention": "Smartphone Addiction", "relationship": "increases", "outcome": "Anxiety"}
      ]
    }

    OUTPUT ONLY THE RAW JSON OBJECT. DO NOT INCLUDE MARKDOWN CODEBLOCKS OR EXPLANATIONS.
    """

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost", 
        "X-Title": "KnowledgeGraphPipeline"  
    }

    files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    print(f"Found {len(files)} files to process.\n")

    for index, filename in enumerate(files, start=1):
        file_path = os.path.join(input_dir, filename)
        print(f"\n[{index}/{len(files)}] Analyzing {filename}...")

        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            
        # Break the text into 8,000 character chunks. 
        # We will process up to the first 3 chunks (24,000 chars) to reach the 'Results' sections.
        chunk_size = 8000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        paper_triplets_count = 0

        for chunk_idx, chunk in enumerate(chunks):
            payload = {
                "model": "openrouter/free", 
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract intervention-outcome triplets from the text below:\n\n{chunk}"}
                ],
                "temperature": 0.0
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                
                data = response.json()
                raw_content = data['choices'][0]['message'].get('content')
                
                if not raw_content:
                    continue

                # REGEX FIX: Surgically hunt for the JSON dictionary, ignoring all conversational fluff
                json_match = re.search(r'\{[\s\S]*\}', raw_content)
                
                if json_match:
                    clean_content = json_match.group(0)
                    parsed_json = json.loads(clean_content)
                    triplets = parsed_json.get("triplets", [])
                    
                    for triplet in triplets:
                        triplet["source_paper"] = filename
                        master_graph_data.append(triplet)
                        paper_triplets_count += 1
                else:
                    print(f"  -> Chunk {chunk_idx + 1}: Could not find valid JSON format.")

            except Exception as e:
                # Silently catch chunk errors so the loop keeps moving
                pass

            # Pause between chunks to respect rate limits
            time.sleep(5)

        print(f"  -> Success: Extracted {paper_triplets_count} total triplets from paper.")

    # Save the final dataset to disk
    with open(output_file, 'w', encoding='utf-8') as out_file:
        json.dump(master_graph_data, out_file, indent=4)

    print("\n" + "="*50)
    print(f"Pipeline complete! Extracted an upgraded total of {len(master_graph_data)} triplets.")
    print(f"Saved successfully to {output_file}")
    print("="*50 + "\n")

if __name__ == "__main__":
    process_all_papers()