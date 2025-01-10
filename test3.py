import requests
from bs4 import BeautifulSoup
import json
import datetime
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

# Function to scrape a single article
def scrape_article(article_url):
    try:
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract the article details
        title = soup.find("h1").text.strip() if soup.find("h1") else None
        author = soup.find(class_="author_name").text.strip() if soup.find(class_="author_name") else "Unknown"
        description = soup.find("meta", {"name": "description"})["content"].strip() if soup.find("meta", {"name": "description"}) else None
        article_content = " ".join([p.text for p in soup.find_all("p")])  # All paragraphs combined
        published_date = soup.find("time")["datetime"] if soup.find("time") else None
        image = soup.find("img", {"class": "featured-image"})["src"] if soup.find("img", {"class": "featured-image"}) else None

        # Return the data in the desired format
        return {
            'title': title,
            'author': author,
            'description': description,
            'text': article_content,
            'link': article_url,
            'published_date': published_date,
            'image_link': image
        }

    except Exception as e:
        print(f"Error scraping {article_url}: {e}")
        return None

# Function to crawl a section of the site and get articles
def crawl_section(section_url, domain, article_path_pattern):
    try:
        response = requests.get(section_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all article links in the section
        articles = []
        
        for link in soup.find_all("a", href=True):
            article_url = link["href"]
            
            # Extract the domain from the URL and check if it matches the provided domain
            parsed_url = urlparse(article_url)
            if parsed_url.netloc == domain and article_path_pattern in article_url:
                articles.append(article_url)
        
        return list(set(articles))  # Remove duplicates

    except Exception as e:
        print(f"Error crawling section {section_url}: {e}")
        return []

# Function to fetch the sitemap URLs
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

# Main function to crawl and save articles in JSON format
def main():
    sitemap_url = "https://www.aajtak.in/rssfeeds/sitemap.xml"  # Example sitemap URL (can be replaced)
    
    # Extract domain from the sitemap URL
    parsed_sitemap_url = urlparse(sitemap_url)
    domain = parsed_sitemap_url.netloc
    
    # Define the article path pattern (can be replaced based on the site you're crawling)
    article_path_pattern = "/story/"  # For AajTak, you can change it as needed
    
    # Fetch the sitemap URLs
    sitemap_urls = fetch_sitemap(sitemap_url)
    
    all_articles = []
    
    for section_url in sitemap_urls:
        print(f"Crawling section: {section_url}")
        article_links = crawl_section(section_url, domain, article_path_pattern)
        
        print(f"Found {len(article_links)} articles in {section_url}")
        
        for article_url in article_links:
            article_data = scrape_article(article_url)
            if article_data:
                all_articles.append(article_data)
    
    # Save all articles to a JSON file
    output_file = f"articles_{domain}_{datetime.datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    
    print(f"Saved {len(all_articles)} articles to {output_file}")

if __name__ == "__main__":
    main()
