# LLM-Driven Knowledge Graph: Digital Media Addiction & Well-Being

**Author:** Muhammed Razi Mullappalli  
**Matriculation Number:** 100004340  
**Institution:** SRH University Heidelberg  
**Course:** Case Study 2 (Applied Data Science and Artificial Intelligence)

---

## 📌 Project Overview
This repository contains a complete end-to-end data engineering and Natural Language Processing (NLP) pipeline. It extracts unstructured clinical findings from 21 scientific peer-reviewed papers regarding digital media addiction, uses zero-shot LLM prompting to structure the relationships, semantically normalizes the entities using vector embeddings, and visualizes the findings via a Natural Language "Insight Engine" built with Streamlit and PyVis.

**Validation Score:** The extraction pipeline achieved an **88.7% F1-Score** (90.0% Precision, 87.5% Recall) based on rigorous manual validation.

---

## 📂 Repository Structure

Below is the complete file and directory architecture for this project:

```text
LITERATURE_MINING_LLM_DRIVEN_KNOWLEDGE_GRAPH/
├── data/
│   ├── clean_text/                     # Parsed, machine-readable text files
│   ├── processed_xml/                  # Intermediate XML files from PDF ingestion
│   ├── raw_pdfs/                       # Original 21 peer-reviewed scientific publications
│   ├── knowledge_graph.html            # Auto-generated PyVis interactive graph artifact
│   ├── manual_validation_sample.csv    # Randomly sampled subset for precision/recall grading
│   ├── master_graph_data.json          # Raw, uncleaned intervention-outcome triplets from LLM
│   └── normalized_graph_data.json      # Final, semantically merged and cleaned JSON dataset
├── lib/                                # Local PyVis & frontend dependencies
│   ├── bindings/
│   ├── tom-select/
│   └── vis-9.1.2/
├── .env                                # Environment variables (OpenRouter LLM API & Pinecone Vector DB Keys)
├── app.py                              # Main Streamlit dashboard & NLP query engine
├── evaluation.py                       # Script to generate validation samples & calculate F1-score
├── extraction.py                       # Core LLM zero-shot prompting and JSON generation script
├── graph_analysis.py                   # NetworkX script calculating Degree & Betweenness Centrality
├── ingestion.py                        # Pipeline entry point: PDF to XML/Text processing
├── knowledge_graph.html                # Root-level auto-generated Streamlit HTML artifact
├── normalization.py                    # Semantic clustering & deduplication script using Pinecone Vector Database
└── xml_parser.py                       # Helper functions to clean academic PDF layout structures
```

## 🛠️ Pipeline Execution Modules
The Python scripts in this repository are designed to be executed sequentially:

**1. Data Ingestion (`ingestion.py` & `xml_parser.py`)**

- Extracts complex academic layouts from the `data/raw_pdfs/` directory.
- Converts documents into clean text strings stored in `data/clean_text/` for optimal LLM context window ingestion.

**2. Knowledge Extraction (`extraction.py`)**

- Interfaces with the LLM API (via keys stored in `.env`).
- Processes the clean text to extract directed relationships (Intervention ──► Relationship ──► Outcome).
- Outputs the raw `data/master_graph_data.json`.

**3. Semantic Normalization (`normalization.py`)**

- Connects to a Pinecone Vector Database (via API key in `.env`).
- Generates vector embeddings for all extracted concepts and uses cosine similarity to identify semantically equivalent terms.
- Merges overlapping terminologies (e.g., automatically combining "Smartphone Restriction" and "Screen Time Limitation" into one normalized node).
- Outputs the production-ready `data/normalized_graph_data.json`.

**4. Network Analysis & Validation (`graph_analysis.py` & `evaluation.py`)**

- Applies NetworkX to calculate graph density and node centrality.
- Exports `data/manual_validation_sample.csv` to establish ground-truth accuracy metrics.

**5. The Insight Engine Frontend (`app.py`)**

- A Streamlit web application that serves as the user interface.
- Features an "Ego-Network" PyVis graph renderer.
- Includes a custom Natural Language NLP simulator allowing users to query the graph in plain English.

## ⚙️ How to Run the Backend Pipeline
If you wish to rebuild the knowledge graph from the raw PDFs, execute the scripts in the following order from your terminal:

1. `python ingestion.py` (Parses PDFs to clean text)
2. `python extraction.py` (Calls LLM to extract JSON triplets)
3. `python normalization.py` (Runs Pinecone semantic merging)
4. `python graph_analysis.py` (Calculates network centrality)
5. `python evaluation.py` (Generates validation metrics)

## 🚀 How to Run the Dashboard

**Prerequisites:**
Ensure you have an active Python virtual environment. You will need to install the following dependencies:
*   **Frontend & Graphing:** `streamlit`, `networkx`, `pyvis`, `pandas`
*   **Backend & LLM:** `pinecone-client`, `python-dotenv`, `pydantic`, `sentence-transformers` (or your specific embedding library)

You must also include a `.env` file in the root directory containing your API keys:
OPENROUTER_API_KEY="your_key_here"
PINECONE_API_KEY="your_key_here"

**Launch Command:**
To start the interactive Insight Engine on your local machine, open your terminal, navigate to the root directory, and execute:

```bash
streamlit run app.py
```
