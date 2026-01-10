import json
import os
from tqdm import tqdm
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import spacy

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")  # e.g., "us-east-1"
INDEX_NAME = "dogvet-rag"

# ----------------------------
# Initialize Pinecone client
# ----------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=300,  # spaCy en_core_web_md embeddings are 300-dimensional
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=PINECONE_ENVIRONMENT
        )
    )

# Connect to the index
index = pc.Index(INDEX_NAME)

# ----------------------------
# Load spaCy model
# ----------------------------
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    # If model isn't installed, install it
    os.system("python3 -m spacy download en_core_web_md")
    nlp = spacy.load("en_core_web_md")

# ----------------------------
# Function to embed texts
# ----------------------------
def embed_texts(texts):
    """Embed a list of texts and return a list of vectors."""
    return [nlp(text).vector.tolist() for text in texts]

# ----------------------------
# Load chunks
# ----------------------------
with open("dog_chunks.json", "r", encoding="utf-8") as f:
    dog_chunks = json.load(f)

print(f"Total chunks to upload: {len(dog_chunks)}")

# ----------------------------
# Convert chunks into Pinecone vectors
# ----------------------------
docs = [
    {
        "page_content": chunk["content"],
        "metadata": {
            "title": chunk["title"],
            "url": chunk["url"],
            "chunk_index": chunk["chunk_index"]
        }
    }
    for chunk in dog_chunks
]

# Compute embeddings for all chunks
embeddings = embed_texts([d["page_content"] for d in docs])

# Prepare vectors for Pinecone
vectors = [
    {
        "id": f"{d['metadata']['url']}-{d['metadata']['chunk_index']}",
        "values": emb,
        "metadata": d["metadata"]
    }
    for d, emb in zip(docs, embeddings)
]

# ----------------------------
# Upsert vectors into Pinecone
# ----------------------------
BATCH_SIZE = 100
for i in tqdm(range(0, len(vectors), BATCH_SIZE), desc="Uploading chunks"):
    batch = vectors[i:i + BATCH_SIZE]
    index.upsert(batch)

print("✅ All chunks uploaded to Pinecone using spaCy embeddings!")

