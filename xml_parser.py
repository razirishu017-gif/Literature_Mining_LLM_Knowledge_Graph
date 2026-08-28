import os
from bs4 import BeautifulSoup

def parse_xml_to_text():
    input_dir = "data/processed_xml/"
    output_dir = "data/clean_text/"
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print("Extracting clean text from XML files...")

    # Loop through every XML file in the processed folder
    for filename in os.listdir(input_dir):
        if filename.endswith(".tei.xml"):
            filepath = os.path.join(input_dir, filename)
            
            # Read the XML file
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'xml')

            # Grobid stores the main content inside the <body> tag.
            # We want to extract just the paragraphs (<p>) to ignore references and metadata.
            body = soup.find('body')
            
            if body:
                paragraphs = body.find_all('p')
                # Combine all paragraphs with a double line break
                clean_text = "\n\n".join([p.get_text() for p in paragraphs])

                # Save it as a normal .txt file
                base_name = filename.replace(".tei.xml", ".txt")
                output_path = os.path.join(output_dir, base_name)
                
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(clean_text)
                    
                print(f"Successfully cleaned: {base_name}")
            else:
                print(f"Warning: No body text found in {filename}")

    print("\nAll files parsed! Check the data/clean_text/ folder.")

if __name__ == "__main__":
    parse_xml_to_text()