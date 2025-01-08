import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Define the sitemap URL
sitemap_url = "https://www.aajtak.in/rssfeeds/sitemap.xml"

# Function to fetch the sitemap and parse the XML
def fetch_sitemap(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch the sitemap. Status code: {response.status_code}")
        return None

# Function to parse the sitemap and get the URLs
def parse_sitemap(sitemap):
    tree = ET.ElementTree(ET.fromstring(sitemap))
    root = tree.getroot()

    # Find all <loc> elements, which contain the article URLs
    urls = []
    for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is not None:
            urls.append(loc.text)
    return urls

# Function to scrape an individual article
def scrape_article(url):
    # Request the article page
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the article at {url}. Status code: {response.status_code}")
        return None

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the article's title
    title_tag = soup.find('h1', class_='headline')  # You might need to adjust the class depending on the page structure
    title = title_tag.text.strip() if title_tag else "No title found"

    # Extract the author's name
    author_tag = soup.find('span', class_='author')  # Adjust if necessary
    author = author_tag.text.strip() if author_tag else "No author found"

    # Extract the full text of the article
    content_tag = soup.find('div', class_='article-body')  # This might need to be adjusted
    full_text = content_tag.get_text(separator='\n', strip=True) if content_tag else "No content found"

    # Extract the publication date
    date_tag = soup.find('time')  # Adjust as needed
    pub_date = date_tag.text.strip() if date_tag else "No publishing date found"

    return {
        'title': title,
        'author': author,
        'full_text': full_text,
        'publication_date': pub_date
    }

# Main function to fetch the sitemap and scrape articles
def main():
    # Fetch the sitemap
    sitemap = fetch_sitemap(sitemap_url)
    if sitemap is None:
        return
    
    # Parse the sitemap to get the article URLs
    article_urls = parse_sitemap(sitemap)

    # Scrape each article
    for url in article_urls:
        print(f"Scraping article: {url}")
        article_data = scrape_article(url)
        if article_data:
            print(f"Title: {article_data['title']}")
            print(f"Author: {article_data['author']}")
            print(f"Published on: {article_data['publication_date']}")
            print(f"Full Text: {article_data['full_text'][:300]}...")  # Print the first 300 characters
            print("-" * 80)

if __name__ == "__main__":
    main()
