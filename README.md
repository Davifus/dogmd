# dogmd
# DogMD 🐶💊

DogMD is a veterinary assistant tool that helps answer dog health questions using a combination of **retrieval-augmented generation (RAG)** with **Pinecone** and cloud-based LLMs via **OpenRouter**. It can retrieve relevant information from trusted sources like the **Merck Veterinary Manual** and answer user queries with source attribution.

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