
import requests

# Fetch sitemap
sitemap_url = "https://www.merckvetmanual.com/sitemaps/veterinary-topic.xml.gz"
response = requests.get(sitemap_url)
response.raise_for_status()

# Treat it as plain text (it’s not actually gzipped)
sitemap_content = response.text

# Save to file
with open("veterinary-topic.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_content)

print("Sitemap saved as veterinary-topic.xml")

