import feedparser
import json
from datetime import datetime

def scrape_rss_feed(feed_url):
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    
    # Check if the feed was successfully parsed
    if feed.bozo:
        print(f"Error parsing the feed: {feed_url}")
        return []
    
    articles = []
    
    # Loop through all the entries (articles) in the RSS feed
    for entry in feed.entries:
        title = entry.get('title', 'No title available')
        link = entry.get('link', 'No link available')
        summary = entry.get('summary', 'No summary available')
        published = entry.get('published', 'No published date available')
        
        # Convert published date to a readable format
        if isinstance(published, str):
            published_date = published
        else:
            # If published is a time structure, format it
            published_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S')
        
        article_info = {
            'title': title,
            'link': link,
            'summary': summary,
            'published_date': published_date
        }
        
        articles.append(article_info)
    
    return articles

def scrape_multiple_feeds(feed_urls):
    all_articles = []
    
    for feed_url in feed_urls:
        articles = scrape_rss_feed(feed_url)
        all_articles.extend(articles)
    
    return all_articles

def save_to_json(data, filename):
    # Save the article data to a JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # List of RSS feed URLs
    rss_feed_urls = [
        "https://feeds.feedburner.com/ndtvnews-top-stories",  # Example: CNN's RSS feed
        "https://www.thehindu.com/news/national/feeder/default.rss",  # Example: New York Times RSS feed
        "https://www.news18.com/commonfeeds/v1/eng/rss/india.xmll"  # Example: BBC News RSS feed
    ]
    
    # Scrape the articles from multiple feeds
    articles = scrape_multiple_feeds(rss_feed_urls)
    
    # Save the articles to a JSON file
    save_to_json(articles, 'articles.json')

    print(f"Scraped data from {len(rss_feed_urls)} feeds and saved to 'articles.json'.")
