import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import pandas as pd
import json

def cluster_news_articles(articles, min_similarity=0.3, min_articles=2):
    """
    Cluster news articles based on content similarity using TF-IDF and DBSCAN.
    
    Parameters:
    articles (list): List of dictionaries with 'title' and 'content' keys
    min_similarity (float): Minimum similarity threshold (0-1)
    min_articles (int): Minimum articles to form a cluster
    
    Returns:
    dict: Clustered articles with cluster labels and key terms
    """
    # Load SpaCy model for NER and keyword extraction
    nlp = spacy.load("en_core_web_sm")
    
    def preprocess_text(text):
        """Remove stopwords and extract important entities/noun phrases"""
        doc = nlp(text)
        # Keep named entities, noun phrases, and important verbs
        important_tokens = []
        
        # Add named entities
        important_tokens.extend([ent.text for ent in doc.ents])
        
        # Add noun phrases
        important_tokens.extend([chunk.text for chunk in doc.noun_chunks])
        
        # Add important verbs (excluding auxiliaries)
        important_tokens.extend([token.lemma_ for token in doc 
                               if token.pos_ == "VERB" and not token.is_stop])
        
        return " ".join(important_tokens)
    
    # Combine title and content with more weight on title
    processed_texts = [
        preprocess_text(article['title'] + " " + article['title'] + " " + article['content'])
        for article in articles
    ]
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(processed_texts)
    
    # Calculate similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Cluster using DBSCAN
    eps = 1 - min_similarity  # Convert similarity threshold to distance
    clustering = DBSCAN(
        eps=eps,
        min_samples=min_articles,
        metric='precomputed'
    ).fit(1 - similarity_matrix)  # Convert similarity to distance
    
    # Extract key terms for each cluster
    def get_cluster_keywords(cluster_docs, top_n=5):
        """Get most important terms for a cluster"""
        if len(cluster_docs) == 0:
            return []
        
        cluster_text = " ".join(cluster_docs)
        doc = nlp(cluster_text)
        
        # Count term frequencies
        term_freq = {}
        for ent in doc.ents:
            if ent.label_ in ['EVENT', 'ORG', 'PERSON', 'LOC', 'GPE']:
                term_freq[ent.text] = term_freq.get(ent.text, 0) + 1
                
        # Sort by frequency
        sorted_terms = sorted(term_freq.items(), key=lambda x: x[1], reverse=True)
        return [term[0] for term in sorted_terms[:top_n]]
    
    # Organize results
    clusters = {}
    for idx, label in enumerate(clustering.labels_):
        if label == -1:  # Noise points
            continue
            
        if label not in clusters:
            clusters[label] = {
                'articles': [],
                'key_terms': []
            }
        
        clusters[label]['articles'].append(articles[idx])
    
    # Add key terms for each cluster
    for label in clusters:
        cluster_texts = [art['content'] for art in clusters[label]['articles']]
        clusters[label]['key_terms'] = get_cluster_keywords(cluster_texts)
    
    return clusters
with open('articles.json') as f:
    sample_articles = json.load(f)


clustered_news = cluster_news_articles(sample_articles)
for cluster_label, cluster_data in clustered_news.items():
    print(f"Cluster {cluster_label} - Key terms: {cluster_data['key_terms']}")
    for article in cluster_data['articles']:
        print(f"\t{article['title']}")