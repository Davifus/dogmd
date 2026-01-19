import requests
import os
from dotenv import load_dotenv
import spacy
from pinecone import Pinecone


#environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "dogvet-rag"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# OpenRouter LLM call
def query_openrouter_chat(
    messages,
    model="openai/gpt-4o-mini",
    max_tokens=512,
    temperature=0.0
):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "DogVet RAG"
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


#Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)


#spaCy (embeddings)
nlp = spacy.load("en_core_web_md")


#user input
usertext = input("Enter your dog health question: ").strip()


#Embed user input
embedding = nlp(usertext).vector.tolist()


#Query Pinecone
TOP_K = 5
SCORE_THRESHOLD = 0.75  

results = index.query(
    vector=embedding,
    top_k=TOP_K,
    include_metadata=True
)



#Filter results by score
filtered_matches = [
    m for m in results["matches"]
    if m["score"] >= SCORE_THRESHOLD
]

if not filtered_matches:
    print("\nNo chunks met the similarity threshold. Try rephrasing your question.")
    exit()


#context
context_texts = []
for match in filtered_matches:
    meta = match["metadata"]
    context_texts.append(
        f"Title: {meta.get('title', 'N/A')}\n"
        f"Source: {meta.get('source', 'N/A')}\n"
        f"{meta.get('text', '')}"
    )

context = "\n\n---\n\n".join(context_texts)


#Build chat messages
messages = [
    {
        "role": "system",
        "content": (
            "You are a veterinary assistant. Answer the user's question using the context provided. "
            "If the context doesn't cover it, give general safe guidance but indicate that the user should consult a vet."

        )
    },
    {
        "role": "user",
        "content": (
            f"Context:\n{context}\n\n"
            f"Question: {usertext}\n"
            f"Answer with source attribution."
        )
    }
]


#Call OpenRouter LLM
answer = query_openrouter_chat(messages)

print("\n--- LLM Answer ---\n")
print(answer)
