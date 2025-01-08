import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime

def get_scraping_task():
    """Request scraping task from the central system."""
    response = requests.get('http://localhost:5000/get_scraping_task')  # Change URL to your central system
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching scraping task.")
        return None

def scrape_rss_feed(url):
    """Scrape RSS feed and extract title, link, description, author, publish date, and full text."""
    print(f"Scraping RSS feed from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        for item in items:
            title = item.find('title').text if item.find('title') else None
            link = item.find('link').text if item.find('link') else None
            description = item.find('description').text if item.find('description') else None
            author = item.find('author').text if item.find('author') else 'Unknown'
            pub_date = item.find('pubDate').text if item.find('pubDate') else None

            # Extract full text from the linked article if necessary
            full_text = None
            if link:
                full_text = scrape_article_details(link)

            # Print out or store the extracted information
            print(f"Title: {title}")
            print(f"Link: {link}")
            print(f"Description: {description}")
            print(f"Author: {author}")
            print(f"Published on: {pub_date}")
            print(f"Full Text: {full_text}")
            print('-' * 50)
    else:
        print(f"Failed to retrieve the RSS feed from {url}")

def scrape_sitemap(url):
    """Scrape sitemap.xml and extract all URLs."""
    print(f"Scraping sitemap from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()
        for url in root.findall('.//url/loc'):
            article_url = url.text
            print(f"Found URL: {article_url}")
            scrape_article_details(article_url)
    else:
        print(f"Failed to retrieve the sitemap from {url}")

def scrape_article_details(url):
    """Scrape the full details of an article: full text, author, publish date."""
    print(f"Scraping article details from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Example: Extracting text from the article
        article_text = soup.find('div', class_='article-body')  # Adjust selector based on website's structure
        full_text = article_text.text.strip() if article_text else 'No full text available'

        # Example: Extracting author name (adjust the selector based on the site)
        author = soup.find('span', class_='author-name')  # Adjust selector based on website's structure
        author_name = author.text.strip() if author else 'Unknown Author'

        # Example: Extracting publish date
        pub_date = soup.find('time', class_='publish-date')  # Adjust selector based on website's structure
        publish_date = pub_date['datetime'] if pub_date else 'Unknown Date'

        # Return the scraped details
        return {
            'full_text': full_text,
            'author': author_name,
            'publish_date': publish_date
        }
    else:
        print(f"Failed to retrieve the article from {url}")
        return None

def scraper():
    task = get_scraping_task()
    if not task:
        return
    
    url = task['url']
    scrape_type = task['scrape_type']

    if scrape_type == 'rss':
        scrape_rss_feed(url)
    elif scrape_type == 'sitemap':
        scrape_sitemap(url)
    else:
        print(f"Unknown scrape type: {scrape_type}")

if __name__ == "__main__":
    scraper()
