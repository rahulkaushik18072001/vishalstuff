import requests
from bs4 import BeautifulSoup
import json
import datetime
import xml.etree.ElementTree as ET

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
def crawl_section(section_url):
    try:
        response = requests.get(section_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all article links in the section
        articles = []
        for link in soup.find_all("a", href=True):
            article_url = link["href"]
            if article_url.startswith("https://www.aajtak.in/") and "/story/" in article_url:
                articles.append(article_url)
        
        return list(set(articles))  # Remove duplicates

    except Exception as e:
        print(f"Error crawling section {section_url}: {e}")
        return []
        
def fetch_sitemap(url): #a function to fetch the urls from the sitemap.xml url, basically convert the xml to individual urls
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
# Main function to crawl AajTak and save articles in JSON format
def main():
    sitemap_urls = fetch_sitemap('https://www.aajtak.in/rssfeeds/sitemap.xml')
    
    all_articles = []
    
    for section_url in sitemap_urls:
        print(f"Crawling section: {section_url}")
        article_links = crawl_section(section_url)
        
        print(f"Found {len(article_links)} articles in {section_url}")
        
        for article_url in article_links:
            article_data = scrape_article(article_url)
            if article_data:
                all_articles.append(article_data)
    
    # Save all articles to a JSON file
    output_file = f"aajtak_articles_{datetime.datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    
    print(f"Saved {len(all_articles)} articles to {output_file}")

if __name__ == "__main__":
    main()