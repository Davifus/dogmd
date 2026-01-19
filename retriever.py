import spacy
import os
import requests
from pinecone import Pinecone
from dotenv import load_dotenv


#environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "dogvet-rag"


#LMStudio chat/completions endpoint
LMSTUDIO_URL = "http://192.168.68.70:1234/v1/chat/completions" #use your LMStudio server address

def query_lmstudio_chat(messages, max_tokens=512, temperature=0.0):
    """
    Sends a chat message list to LMStudio and returns the generated text.
    """
    payload = {
        "model": "",  
        "messages": messages,
        "max_new_tokens": max_tokens,
        "temperature": temperature
    }
    response = requests.post(LMSTUDIO_URL, json=payload)
    response.raise_for_status()
    
    return response.json()["choices"][0]["message"]["content"]


#Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)


#spaCy (prototyping embeddings)
nlp = spacy.load("en_core_web_md")

#user input
usertext = input("Enter your dog health question: ")


#Embed user input
embedding = nlp(usertext).vector.tolist()


#Query Pinecone
TOP_K = 5
SCORE_THRESHOLD = 0.7

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

#context for LMStudio
if not filtered_matches:
    print("No chunks met the similarity threshold. Try rephrasing your question.")
else:
    context_texts = []
    for match in filtered_matches:
        metadata = match.get('metadata', {})
        source = metadata.get('source', 'unknown')
        snippet = metadata.get('text', '')
        context_texts.append(f"Source: {source}\n{snippet}")

    context = "\n\n".join(context_texts)

    #Build chat messages
    messages = [
        {
            "role": "system",
            "content": (
                "You are a veterinary assistant. Answer the user's question "
                "using ONLY the context provided. Do NOT make up information. "
                "If the answer isn't in the context, say you don't know."
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {usertext}\nAnswer with source attribution."
        }
    ]

    #LMStudio chat
    answer = query_lmstudio_chat(messages)
    print("\n--- LLM Answer ---\n")
    print(answer)








