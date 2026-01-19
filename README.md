# DogMD 🐶💊

DogMD is a Retrieval-Augmented Generation (RAG) project designed to answer dog health questions using trusted veterinary sources. It combines a vector database with a cloud-based language model to provide context-aware answers with source attribution.

The project workflow:

User Query: Users ask a question about dog health.

Vector Search: The query is converted into embeddings using spaCy and matched against a Pinecone vector database containing chunks of veterinary content.

Contextual LLM Response: The relevant text chunks are passed to a cloud LLM via OpenRouter API, which generates a concise answer while citing sources.

## Optional
- ETL with Prefect: Automate ingestion of new veterinary content from sources like Merck Veterinary Manual, transforming and pushing it into Pinecone.

---

## Features

- Search and retrieve relevant veterinary knowledge from a vector database (Pinecone).
- Use **OpenRouter API** to query LLMs (like `gpt-4o-mini`) for context-based answers.
- Provide answers **with source attribution**, only using available context.
- Easy local setup with Python and `.env` support for API keys.
- Designed to be extended into a web interface or React frontend.

---

## Prerequisites

- Python 3.10+
- `pip` package manager
- Pinecone account & API key
- OpenRouter API key
- LMStudio

---

## Installation

1. Clone the repo:

git clone https://github.com/yourusername/DogMD.git
cd DogMD

2. Create and activate a virtual environment (optional but recommended):

python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

3. Install dependencies:
pip install -r requirements.txt

4. Run it
Run the main Python script to ask dog health questions:

python cloud_retriever.py (for openrouter/cloud llm)
python retriever.py (for lmstudio)

LLM answer based on retrieved context with source attribution.
