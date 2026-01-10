import json

# Load scraped dog pages
with open("dog_pages.json", "r", encoding="utf-8") as f:
    dog_pages = json.load(f)

print(f"Total scraped pages: {len(dog_pages)}")

# Preview first page
first_page = dog_pages[0]
print("Title:", first_page["title"])
print("URL:", first_page["url"])
print("Content preview:", first_page["content"][:500], "...")  # first 500 chars

# ----------------------------
# Dog keyword bank for filtering
# ----------------------------
dog_keywords = [
    "dog", "dogs", "canine", "puppy", "puppies", "k9", "hound", "pooch", "pooches", "mutt", "mutts",
    "pup", "doggy", "doggo",
    "labrador", "lab", "german-shepherd", "golden-retriever", "beagle",
    "bulldog", "poodle", "rottweiler", "yorkshire-terrier", "boxer",
    "dachshund", "husky", "doberman", "shih-tzu", "chihuahua", "great-dane",
    "pomeranian", "border-collie", "mastiff", "cocker-spaniel", "dalmatian",
    "boston-terrier", "australian-shepherd", "bernese"
]

# Filter pages that mention any dog-related keyword
filtered_pages = [
    page for page in dog_pages
    if any(kw in page["content"].lower() for kw in dog_keywords)
]

print(f"Pages after filtering: {len(filtered_pages)}")

# Optional: save filtered pages
with open("dog_pages_filtered.json", "w", encoding="utf-8") as f:
    json.dump(filtered_pages, f, indent=2)

print("Filtered dog pages saved to dog_pages_filtered.json")
