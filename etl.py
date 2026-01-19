from prefect import flow, task, get_run_logger
import requests
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import spacy
import gzip
from io import BytesIO
import hashlib


#global variables
#SOURCE_NAME = "Merck Veterinary Manual" #test source 
#SITEMAP_URL = "https://www.merckvetmanual.com/sitemaps/veterinary-topic.xml.gz" #test website

CHUNK_SIZE_TOKENS = 500
CRAWL_DELAY_SECONDS = 5

INDEX_NAME = "dogvet-rag"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DogVetBot/1.0)"
}


# Global SpaCy model
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    os.system("python3 -m spacy download en_core_web_md")
    nlp = spacy.load("en_core_web_md")
    

# Full dog keyword bank (general names + popular breeds)
dog_keywords = [
    "dog", "dogs", "canine", "puppy", "puppies", "k9", "hound", "pooch", "pooches", "mutt", "mutts",
    "pup", "canids", "doggy", "doggo",
    "labrador", "labrador-retriever", "lab", "labs",
    "german-shepherd", "shepherd",
    "golden-retriever", "golden",
    "beagle", "beagles",
    "bulldog", "bulldogs", "english-bulldog", "french-bulldog",
    "poodle", "poodles",
    "rottweiler", "rottweilers",
    "yorkshire-terrier", "yorkie", "yorkies",
    "boxer", "boxers",
    "dachshund", "dachshunds", "sausage-dog",
    "siberian-husky", "husky", "huskies",
    "doberman", "dobermans", "dobie",
    "shih-tzu", "shih-tzus",
    "chihuahua", "chihuahuas",
    "great-dane", "great-danes",
    "pomeranian", "pomeranians",
    "border-collie", "collie", "collies",
    "mastiff", "mastiffs",
    "cocker-spaniel", "spaniel", "spaniels",
    "dalmatian", "dalmatians",
    "boston-terrier", "boston-terriers",
    "australian-shepherd", "aussie", "aussies",
    "bernese-mountain-dog", "bernese"
]


@task
def extract(sitemap_url: str) -> str:
    response = requests.get(sitemap_url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    
    data = response.content
    
    try:
        with gzip.open(BytesIO(data), "rt", encoding="utf-8") as f:
            return f.read()
    except (OSError, gzip.BadGzipFile):
        return data.decode("utf-8")

    return response.text


@task
def transform(sitemap_content: str) -> list[str]:
    import xml.etree.ElementTree as ET

    # Parse XML
    root = ET.fromstring(sitemap_content)

    # Filter dog URLs
    dog_urls = [
        u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        for u in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        if any(kw in u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text.lower() for kw in dog_keywords)
    ]
    return dog_urls

@task
def extract_pages(dog_urls: list[str]) -> list[dict]:
    scraped_data = []
    logger = get_run_logger()  
    for i, url in enumerate(dog_urls):
        logger.info(f"[{i+1}/{len(dog_urls)}] Scraping {url}")  

        try:
            response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("h1")
        paragraphs = soup.find_all("p")

        scraped_data.append({
            "url": url,
            "title": title.get_text(strip=True) if title else "",
            "content": "\n".join(p.get_text(strip=True) for p in paragraphs),
        })

        time.sleep(CRAWL_DELAY_SECONDS)  # crawl-delay
        

    return scraped_data
        
@task
def transform_pages(scraped_data: list[dict]) -> list[dict]:
    # Filter pages that mention any dog-related keyword
    filtered_pages = [
        page for page in scraped_data
        if any(kw in page["content"].lower() for kw in dog_keywords)
    ]

    #helper Function to split text into chunks
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

    all_chunks = []

    for page in filtered_pages:
        content = page["content"]
        chunks = split_into_chunks(content, CHUNK_SIZE_TOKENS) 
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "title": page["title"],
                "url": page["url"],
                "chunk_index": i,
                "content": chunk
        })
            
    return all_chunks
    
@task
def load(data: list, source_name: str):
    #local environment variables
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")  # e.g., "us-east-1"
    
    #initialize Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create index if it doesn't exist
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=300,  # spaCy en_core_web_md embeddings are 300-dimensional
            #dim = len(nlp("test").vector)
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=PINECONE_ENVIRONMENT
            )
        )
    # Connect to the index
    index = pc.Index(INDEX_NAME)
    
    # Function to embed texts
    def embed_texts(texts):
        return [nlp(text).vector.tolist() for text in texts]
    
    docs = [
        {
            "page_content": chunk["content"],
            "metadata": {
                "title": chunk.get("title", ""),
                "url": chunk.get("url", ""),
                "chunk_index": chunk.get("chunk_index", i),
                "source": source_name,      
                "text": chunk["content"][:1000]  # <-- snippet for sanity tests
            }
        }
        for i, chunk in enumerate(data)
    ]
    
    
    # Compute embeddings for all chunks
    embeddings = embed_texts([d["page_content"] for d in docs])

    def make_id(url, chunk_index):
        return hashlib.md5(f"{url}-{chunk_index}".encode()).hexdigest()

    # Prepare vectors for Pinecone
    vectors = [
        {
            "id": make_id(d["metadata"]["url"], d["metadata"]["chunk_index"]),
            "values": emb,
            "metadata": d["metadata"]
        }
        for d, emb in zip(docs, embeddings)
    ]
            
    #upsert vectors in batches
    logger = get_run_logger()  # Prefect logger

    BATCH_SIZE = 100
    total_batches = (len(vectors) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num, i in enumerate(range(0, len(vectors), BATCH_SIZE), start=1):
        batch = vectors[i:i + BATCH_SIZE]
        index.upsert(vectors=batch)
        logger.info(f"Uploaded batch {batch_num}/{total_batches} ({len(batch)} vectors)")
    
@flow
def etl_flow(source_name: str, sitemap_url: str):
    logger = get_run_logger()
    logger.info(f"Starting ETL for source: {source_name}, sitemap: {sitemap_url}")

    sitemap = extract(sitemap_url)
    dog_urls = transform(sitemap)
    scraped_pages = extract_pages(dog_urls)
    chunks = transform_pages(scraped_pages)
    load(chunks, source_name)



if __name__ == "__main__":
    etl_flow.deploy(
        name="DogVet ETL",
        work_pool_name="docker-pool",
        work_queue_name="dogvet-queue",
        image="davifus/dogvet-etl:latest",
        build=False,   # Important: don't try to rebuild
        push=False     # Already pushed manually
    )

