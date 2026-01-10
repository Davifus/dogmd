import json
import math

# Load filtered dog pages
with open("dog_pages_filtered.json", "r", encoding="utf-8") as f:
    dog_pages = json.load(f)

print(f"Total filtered pages: {len(dog_pages)}")

# ----------------------------
# Function to split text into chunks
# ----------------------------
def split_into_chunks(text, chunk_size_tokens=500):
    # Approximation: 1 token ~ 4 characters
    chunk_size_chars = chunk_size_tokens * 4
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size_chars
        chunk_text = text[start:end]
        chunks.append(chunk_text.strip())
        start = end
    return chunks

# ----------------------------
# Split pages into chunks
# ----------------------------
all_chunks = []

for page in dog_pages:
    content = page["content"]
    chunks = split_into_chunks(content, chunk_size_tokens=500)  # ~500 tokens per chunk
    for i, chunk in enumerate(chunks):
        all_chunks.append({
            "title": page["title"],
            "url": page["url"],
            "chunk_index": i,
            "content": chunk
        })

print(f"Total chunks created: {len(all_chunks)}")

# ----------------------------
# Save chunks to JSON
# ----------------------------
with open("dog_chunks.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2)

print("Chunks saved to dog_chunks.json")
