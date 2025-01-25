import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import json
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

def cluster_news_articles(articles, similarity_threshold=0.5, min_cluster_size=2):
    """
    Cluster news articles using sentence transformers and hierarchical clustering.
    
    Parameters:
    articles (list): List of dictionaries with 'title' and 'content' keys
    similarity_threshold (float): Threshold for clustering (0-1)
    min_cluster_size (int): Minimum number of articles per cluster
    
    Returns:
    tuple: (clusters dict, unclustered articles list)
    """
    # Load models
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, fast model
    nlp = spacy.load("en_core_web_sm")
    
    def prepare_text(title, content):
        """Prepare text for embedding"""
        # Combine title and first few sentences of content
        doc = nlp(content)
        first_sentences = list(doc.sents)[:3]  # Take first 3 sentences
        important_content = ' '.join([sent.text for sent in first_sentences])
        
        # Weighted combination of title and content
        return f"{title} {title} {important_content}"
    
    # Prepare texts
    texts = [prepare_text(article['title'], article['content']) for article in articles]
    
    # Generate embeddings
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Calculate similarity matrix
    similarity_matrix = cosine_similarity(embeddings)
    
    # Convert similarity to distance
    distance_matrix = 1 - similarity_matrix
    
    # Perform hierarchical clustering
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=1 - similarity_threshold,
        metric='precomputed',
        linkage='complete'
    )
    
    cluster_labels = clustering.fit_predict(distance_matrix)
    
    # Organize results
    clusters = {}
    unclustered = []
    
    # Count articles per cluster
    from collections import Counter
    cluster_counts = Counter(cluster_labels)
    
    # Assign articles to clusters or unclustered
    for idx, label in enumerate(cluster_labels):
        # If cluster is too small, mark as unclustered
        if cluster_counts[label] < min_cluster_size:
            unclustered.append(articles[idx])
            continue
            
        if label not in clusters:
            clusters[label] = {
                'articles': [],
                'avg_similarity': []
            }
        
        # Calculate average similarity with other articles in cluster
        cluster_indices = np.where(cluster_labels == label)[0]
        avg_sim = np.mean([similarity_matrix[idx][j] for j in cluster_indices if j != idx])
        
        clusters[label]['articles'].append(articles[idx])
        clusters[label]['avg_similarity'].append(avg_sim)
    
    # Sort articles within each cluster by similarity
    for label in clusters:
        sorted_indices = np.argsort(clusters[label]['avg_similarity'])[::-1]
        clusters[label]['articles'] = [clusters[label]['articles'][i] for i in sorted_indices]
    
    return clusters, unclustered

def visualize_clustering(similarity_matrix, labels):
    """Visualize the clustering results"""
    plt.figure(figsize=(10, 7))
    plt.imshow(similarity_matrix, cmap='viridis')
    plt.colorbar()
    plt.title('Article Similarity Matrix')
    plt.savefig('similarity_matrix.png')
    plt.close()

# Example usage
if __name__ == "__main__":
    # Load articles
    with open('articles.json') as f:
        sample_articles = json.load(f)

    print(f"Total articles: {len(sample_articles)}")
    
    # Try different similarity thresholds
    for threshold in [0.3, 0.5, 0.7]:
        print(f"\nTrying similarity threshold: {threshold}")
        print("-" * 50)
        
        clusters, unclustered = cluster_news_articles(
            sample_articles,
            similarity_threshold=threshold,
            min_cluster_size=2
        )
        
        # Print results
        print(f"\nFound {len(clusters)} clusters")
        for cluster_id, cluster_data in clusters.items():
            print(f"\nCluster {cluster_id}:")
            print("Articles (sorted by similarity to cluster):")
            for article in cluster_data['articles']:
                print(f"  - {article['title']}")
        
        if unclustered:
            print(f"\nUnclustered articles ({len(unclustered)}):")
            for article in unclustered:
                print(f"  - {article['title']}")