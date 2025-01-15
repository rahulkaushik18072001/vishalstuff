import json
from transformers import pipeline

def load_articles(json_file):
    with open(json_file, 'r') as file:
        articles = json.load(file)
    return articles

def summarize_article(text, chunk_size=1000):
    summarizer = pipeline('summarization')
    summaries = []
    
    # Split text into chunks
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        summary = summarizer(chunk, max_length=60, min_length=40, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    
    return summaries

if __name__ == "__main__":
    json_file = "./articles.json"
    articles = load_articles(json_file)
    
    for i, article in enumerate(articles):
        print(f"\nSummarizing article {i+1}...")
        text = article['content']
        summaries = summarize_article(text)
        print(f"Summaries: {summaries}")

