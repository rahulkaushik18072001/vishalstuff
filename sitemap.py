import requests
import xml.etree.ElementTree as ET

# Function to fetch and parse sitemap XML
def fetch_sitemap(url):
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the XML content
        root = ET.fromstring(response.content)
        
        # Find all <loc> tags in the sitemap and extract their URLs
        urls = [url.text for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        
        return urls
    else:
        print(f"Failed to fetch sitemap. HTTP Status code: {response.status_code}")
        return []

# Define the URL of the sitemap
sitemap_url = 'https://www.aajtak.in/rssfeeds/sitemap.xml'

# Call the function to fetch and parse the sitemap
links = fetch_sitemap(sitemap_url)

# Print the list of links
print("Links found in sitemap:")
for link in links:
    print(link)

# Save the list of links to a file (optional)
with open('sitemap_links.txt', 'w') as f:
    for link in links:
        f.write(link + '\n')

