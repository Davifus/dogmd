from flask import Flask, render_template, request, jsonify
import os
import requests
import spacy
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "dogvet-rag"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize Global Resources (Load once at startup)
print("Initializing Pinecone and spaCy...")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
nlp = spacy.load("en_core_web_md")
print("Ready.")

def query_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "DogVet RAG"
    }
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.0
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please enter a question."})

    #user input
    embedding = nlp(user_message).vector.tolist()

    #Query Pinecone
    results = index.query(
        vector=embedding,
        top_k=5,
        include_metadata=True
    )

    #Filter results
    SCORE_THRESHOLD = 0.75
    matches = [m for m in results["matches"] if m["score"] >= SCORE_THRESHOLD]

    if not matches:
        return jsonify({
            "response": "I couldn't find any relevant veterinary information in my database for that query. Please try rephrasing or consult a vet directly."
        })

    #Build Context
    context_texts = []
    for m in matches:
        meta = m["metadata"]
        context_texts.append(f"Source: {meta.get('source', 'N/A')}\n{meta.get('text', '')}")
    
    context_str = "\n\n---\n\n".join(context_texts)

    #Call LLM
    messages = [
        {
            "role": "system",
            "content": "You are a veterinary assistant. Answer the user's question using the context provided. If the context doesn't cover it, give general safe guidance but indicate that the user should consult a vet."
        },
        {
            "role": "user",
            "content": f"Context:\n{context_str}\n\nQuestion: {user_message}\nAnswer with source attribution."
        }
    ]

    try:
        answer = query_openrouter(messages)
        return jsonify({"response": answer})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "Sorry, I encountered an error contacting the AI model."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)