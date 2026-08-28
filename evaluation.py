import json
import random
import pandas as pd

def create_validation_sample():
    # UPDATED: Now pulling from the normalized graph dataset
    input_file = "data/normalized_graph_data.json"
    output_csv = "data/manual_validation_sample.csv"
    
    print("Loading normalized dataset...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Randomly sample 30 triplets 
    sample_size = min(30, len(data))
    sample = random.sample(data, sample_size)
    
    # Convert to a Pandas DataFrame for easy CSV export
    df = pd.DataFrame(sample)
    
    # Add empty columns for your manual grading
    df['True_Positive (1=Correct, 0=Incorrect)'] = ""
    df['Reviewer_Notes'] = ""
    
    # Save to CSV
    df.to_csv(output_csv, index=False)
    
    print("\n" + "="*50)
    print(f"Success! Randomly sampled {sample_size} normalized triplets.")
    print(f"Saved grading sheet to: {output_csv}")
    print("="*50)
    print("Next Steps:")
    print("1. Open the CSV in Excel or Google Sheets.")
    print("2. Read the extracted triplet and check the original source paper.")
    print("3. Type '1' if the pipeline extracted it correctly, or '0' if it hallucinated.")

if __name__ == "__main__":
    create_validation_sample()