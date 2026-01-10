import xml.etree.ElementTree as ET
import json

# Load sitemap XML
with open("veterinary-topic.xml", "r", encoding="utf-8") as f:
    sitemap_content = f.read()

# Parse XML
root = ET.fromstring(sitemap_content)

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

# Filter dog URLs
dog_urls = [
    u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
    for u in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
    if any(kw in u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text.lower() for kw in dog_keywords)
]

print(f"Found {len(dog_urls)} dog-related URLs.")
print(dog_urls[:10])  # Preview first 10

# Save filtered URLs to JSON
with open("dog_urls.json", "w", encoding="utf-8") as f:
    json.dump(dog_urls, f, indent=2)

print("Dog URLs saved to dog_urls.json")
