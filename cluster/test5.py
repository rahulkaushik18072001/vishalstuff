import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import json

def cluster_news_articles(articles, min_similarity=0.3, min_articles=2):
    """
    A generalized approach to cluster news articles based on content similarity.
    
    Parameters:
    articles (list): List of dictionaries with 'title' and 'content' keys
    min_similarity (float): Minimum similarity threshold (0-1)
    min_articles (int): Minimum articles to form a cluster
    
    Returns:
    tuple: (clusters dict, unclustered articles list)
    """
    nlp = spacy.load("en_core_web_sm")
    
    def preprocess_text(title, content):
        """Extract meaningful features from text while maintaining generality"""
        # Process full text
        full_text = f"{title} {title} {content}"  # Weight title by repeating it
        doc = nlp(full_text)
        
        # Extract meaningful words and phrases
        important_terms = []
        
        # Get named entities
        important_terms.extend([ent.text for ent in doc.ents])
        
        # Get noun phrases
        important_terms.extend([chunk.text for chunk in doc.noun_chunks])
        
        # Get main verbs and their associated nouns
        for token in doc:
            if token.pos_ == "VERB" and not token.is_stop:
                important_terms.append(token.lemma_)
                
                # Include associated nouns
                for child in token.children:
                    if child.pos_ in ["NOUN", "PROPN"]:
                        important_terms.append(child.text)
        
        return " ".join(important_terms)
    
    # Process all articles
    processed_texts = [
        preprocess_text(article['title'], article['content'])
        for article in articles
    ]
    
    # Convert text to TF-IDF vectors
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_df=0.9,    # Ignore terms that appear in >90% of docs
        min_df=2,      # Ignore terms that appear in <2 docs
        stop_words='english'
    )
    
    tfidf_matrix = vectorizer.fit_transform(processed_texts)
    
    # Calculate similarity and convert to distance
    similarity_matrix = cosine_similarity(tfidf_matrix)
    distance_matrix = np.clip((1 - similarity_matrix), 0, 2)
    
    # Cluster using DBSCAN
    clustering = DBSCAN(
        eps=1 - min_similarity,
        min_samples=min_articles,
        metric='precomputed'
    ).fit(distance_matrix)
    
    # Organize results
    clusters = {}
    unclustered = []
    
    for idx, label in enumerate(clustering.labels_):
        if label == -1:
            unclustered.append(articles[idx])
            continue
            
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(articles[idx])
    
    return clusters, unclustered

# Example usage
if __name__ == "__main__":
    # Load articles
    with open('articles.json') as f:
        sample_articles = json.load(f)

    print(f"Total articles: {len(sample_articles)}")
    
    # Try different similarity thresholds to find optimal clustering
    for similarity in [0.2, 0.3, 0.4, 0.5]:
        print(f"\nTrying similarity threshold: {similarity}")
        print("-" * 40)
        
        clusters, unclustered = cluster_news_articles(
            sample_articles,
            min_similarity=similarity,
            min_articles=2
        )
        
        # Print results
        print(f"\nFound {len(clusters)} clusters")
        for cluster_id, articles in clusters.items():
            print(f"\nCluster {cluster_id} ({len(articles)} articles):")
            for article in articles:
                print(f"  - {article['title']}")
        
        print(f"\nUnclustered articles: {len(unclustered)}")
        for article in unclustered:
            print(f"  - {article['title']}")