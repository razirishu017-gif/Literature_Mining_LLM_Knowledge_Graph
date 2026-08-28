from grobid_client.grobid_client import GrobidClient
import os

def process_pdfs():
    # 1. Initialize the Grobid client pointing to your local Docker server
    client = GrobidClient(config_path=None)
    client.config = {
        "grobid_server": "http://localhost:8070",
        "batch_size": 1,
        "sleep_time": 5,
        "timeout": 120
    }

    # 2. Define your input and output directories
    input_dir = "data/raw_pdfs/"
    output_dir = "data/processed_xml/"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Sending PDFs from {input_dir} to Grobid server...")

    # 3. Process the full text of the documents
    # 'processFulltextDocument' extracts headers, paragraphs, and structure
    client.process(
        "processFulltextDocument",
        input_dir,
        output_dir,
        consolidate_header=True,
        consolidate_citations=False,
        force=True
    )

    print(f"Extraction complete! Check the {output_dir} folder.")

if __name__ == "__main__":
    process_pdfs()