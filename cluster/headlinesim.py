import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import pandas as pd
import json
from datetime import datetime
import os

class HeadlineClusteringPipeline:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", similarity_threshold: float = 0.6):
        """
        Initialize the headline clustering pipeline.
        Args:
            model_name: Name of the sentence transformer model to use
            similarity_threshold: Threshold for considering headlines similar (0 to 1)
        """
        self.encoder = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold

    def cluster_headlines(self, articles: List[Dict]) -> Dict[int, List[Dict]]:
        """
        Cluster articles based on headline similarity.
        """
        # Extract headlines
        headlines = [article['title'] for article in articles]
        
        # Generate embeddings for headlines
        embeddings = self.encoder.encode(headlines)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(embeddings)
        
        # Initialize clusters
        clusters = {}
        processed = set()
        
        # Create clusters based on similarity
        for i in range(len(articles)):
            if i in processed:
                continue
                
            # Find similar headlines
            similar_indices = np.where(similarity_matrix[i] > self.similarity_threshold)[0]
            
            if len(similar_indices) > 0:
                cluster_id = len(clusters)
                clusters[cluster_id] = []
                
                # Add articles to cluster with their similarity scores
                for idx in similar_indices:
                    if idx not in processed:
                        article_with_score = articles[idx].copy()
                        article_with_score['similarity_score'] = similarity_matrix[i][idx]
                        clusters[cluster_id].append(article_with_score)
                        processed.add(idx)
        
        # Add remaining articles as singletons
        for i in range(len(articles)):
            if i not in processed:
                cluster_id = len(clusters)
                article_with_score = articles[i].copy()
                article_with_score['similarity_score'] = 1.0  # Self-similarity
                clusters[cluster_id] = [article_with_score]
        
        return clusters

    def print_clusters(self, clusters: Dict):
        """Print clusters in a readable format."""
        print("\n=== HEADLINE-BASED NEWS CLUSTERS ===\n")
        
        for cluster_id, articles in clusters.items():
            print(f"\n{'='*50}")
            print(f"📌 CLUSTER {cluster_id}")
            print(f"📊 Number of articles: {len(articles)}")
            print(f"{'='*50}\n")
            
            for idx, article in enumerate(articles, 1):
                print(f"{idx}. {article['title']}")
                print(f"   Similarity Score: {article['similarity_score']:.3f}")
                print(f"   Content preview: {article['content'][:100]}...")
                print()
            
            print(f"{'-'*50}\n")

    def save_clusters_to_json(self, clusters: Dict, output_dir: str = 'output'):
        """Save clusters to a JSON file with timestamp."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'headline_clusters_{timestamp}.json'
        filepath = os.path.join(output_dir, filename)
        
        # Convert numpy float32/64 to Python float for JSON serialization
        clusters_json = {}
        for cluster_id, articles in clusters.items():
            clusters_json[str(cluster_id)] = [
                {
                    **article,
                    'similarity_score': float(article['similarity_score'])
                }
                for article in articles
            ]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clusters_json, f, indent=2, ensure_ascii=False)
            
        return filepath

def example_usage():
    # Sample articles
    with open ('articles.json') as f:
        articles = json.load(f)
    
    # Initialize pipeline
    pipeline = HeadlineClusteringPipeline(similarity_threshold=0.6)
    
    # Cluster articles
    clusters = pipeline.cluster_headlines(articles)
    
    # Print clusters
    pipeline.print_clusters(clusters)
    
    # Save to JSON
    output_file = pipeline.save_clusters_to_json(clusters)
    print(f"\nClusters saved to: {output_file}")

if __name__ == "__main__":
    example_usage()