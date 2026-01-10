import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import time

# ----------------------------
# 1️⃣ Fetch the sitemap XML
# ----------------------------
sitemap_url = "https://www.merckvetmanual.com/sitemaps/veterinary-topic.xml.gz"
print("Fetching sitemap...")
response = requests.get(sitemap_url)
response.raise_for_status()

sitemap_content = response.text  # assuming plain XML
with open("veterinary-topic.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_content)
print("Sitemap saved as veterinary-topic.xml")

# ----------------------------
# 2️⃣ Parse sitemap XML
# ----------------------------
print("Parsing sitemap...")
root = ET.fromstring(sitemap_content)

# ----------------------------
# 3️⃣ Dog keyword bank
# ----------------------------
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

# ----------------------------
# 4️⃣ Filter dog URLs
# ----------------------------
dog_urls = [
    u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
    for u in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
    if any(kw in u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text.lower() for kw in dog_keywords)
]

print(f"Found {len(dog_urls)} dog-related URLs.")
with open("dog_urls.json", "w", encoding="utf-8") as f:
    json.dump(dog_urls, f, indent=2)
print("Dog URLs saved to dog_urls.json")

# ----------------------------
# 5️⃣ Scrape dog pages
# ----------------------------
scraped_data = []

for i, url in enumerate(dog_urls):
    print(f"[{i+1}/{len(dog_urls)}] Scraping {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title_tag = soup.find("h1")
    title_text = title_tag.get_text(strip=True) if title_tag else ""

    # Extract paragraphs
    paragraphs = soup.find_all("p")
    content_text = "\n".join(p.get_text(strip=True) for p in paragraphs)

    scraped_data.append({
        "url": url,
        "title": title_text,
        "content": content_text
    })

    # Respect 5-second crawl-delay
    time.sleep(5)

# ----------------------------
# 6️⃣ Save scraped data
# ----------------------------
with open("dog_pages.json", "w", encoding="utf-8") as f:
    json.dump(scraped_data, f, indent=2)

print(f"Scraped {len(scraped_data)} pages and saved to dog_pages.json")
