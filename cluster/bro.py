import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
import umap
import hdbscan
from typing import List, Dict, Tuple
import pandas as pd
import json
from datetime import datetime
import os

class NewsClusteringPipeline:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the news clustering pipeline.
        Args:
            model_name: Name of the sentence transformer model to use
        """
        # Initialize BERT-based sentence transformer for embeddings
        self.encoder = SentenceTransformer(model_name)
        
        # Initialize BERTopic model with custom parameters
        self.topic_model = BERTopic(
            embedding_model=self.encoder,
            umap_model=umap.UMAP(
                n_neighbors=15,
                n_components=5,
                min_dist=0.0,
                metric='cosine'
            ),
            hdbscan_model=hdbscan.HDBSCAN(
                min_cluster_size=2,
                metric='euclidean',
                cluster_selection_method='eom',
                prediction_data=True
            ),
            verbose=True
        )

    def process_articles(self, articles: List[Dict]) -> Tuple[pd.DataFrame, Dict]:
        """Process and cluster news articles."""
        texts = [f"{art['title']}. {art['content']}" for art in articles]
        topics, probs = self.topic_model.fit_transform(texts)
        
        topic_info = self.topic_model.get_topic_info()
        
        results_df = pd.DataFrame({
            'title': [art['title'] for art in articles],
            'content': [art['content'] for art in articles],
            'topic_id': topics,
            'confidence': probs.max(axis=1) if len(probs.shape) > 1 else probs
        })
        
        topic_mapping = {}
        for topic_id in results_df['topic_id'].unique():
            if topic_id != -1:
                topic_terms = self.topic_model.get_topic(topic_id)
                topic_mapping[topic_id] = [term[0] for term in topic_terms[:5]]
        
        return results_df, topic_mapping

    def format_clusters(self, results_df: pd.DataFrame, topic_mapping: Dict) -> Dict:
        """
        Format clustering results into a readable structure.
        Returns a dictionary with clusters and their articles.
        """
        clusters = {}
        
        # Handle unclustered articles (topic_id = -1)
        unclustered = results_df[results_df['topic_id'] == -1]
        if not unclustered.empty:
            clusters['unclustered'] = {
                'articles': unclustered[['title', 'content', 'confidence']].to_dict('records'),
                'keywords': ['unclustered'],
                'article_count': len(unclustered)
            }
        
        # Handle clustered articles
        for topic_id in topic_mapping.keys():
            cluster_articles = results_df[results_df['topic_id'] == topic_id]
            if not cluster_articles.empty:
                clusters[f'cluster_{topic_id}'] = {
                    'articles': cluster_articles[['title', 'content', 'confidence']].to_dict('records'),
                    'keywords': topic_mapping[topic_id],
                    'article_count': len(cluster_articles)
                }
        
        return clusters

    def save_clusters_to_json(self, clusters: Dict, output_dir: str = 'output'):
        """Save clusters to a JSON file with timestamp."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'news_clusters_{timestamp}.json'
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clusters, f, indent=2, ensure_ascii=False)
            
        return filepath

    def print_clusters(self, clusters: Dict):
        """Print clusters in a readable format."""
        print("\n=== NEWS ARTICLE CLUSTERS ===\n")
        
        for cluster_name, cluster_data in clusters.items():
            print(f"\n{'='*50}")
            print(f"📌 {cluster_name.upper()}")
            print(f"📊 Number of articles: {cluster_data['article_count']}")
            print(f"🔑 Keywords: {', '.join(cluster_data['keywords'])}")
            print(f"{'='*50}\n")
            
            for idx, article in enumerate(cluster_data['articles'], 1):
                print(f"{idx}. {article['title']}")
                print(f"   Confidence: {article['confidence']:.2f}")
                print(f"   Content preview: {article['content'][:100]}...")
                print()
            
            print(f"{'-'*50}\n")

def example_usage():
    # Sample articles
    with open('articles.json') as f:
        articles = json.load(f)
    
    # Initialize pipeline
    pipeline = NewsClusteringPipeline()
    
    # Process articles
    results_df, topic_mapping = pipeline.process_articles(articles)
    
    # Format clusters
    clusters = pipeline.format_clusters(results_df, topic_mapping)
    
    # Print clusters in readable format
    pipeline.print_clusters(clusters)
    
    # Save to JSON file
    output_file = pipeline.save_clusters_to_json(clusters)
    print(f"\nClusters saved to: {output_file}")

if __name__ == "__main__":
    example_usage()
    # Process articles
    results_df, topic_mapping = pipeline.process_articles(articles)
    
    # Format clusters
    clusters = pipeline.format_clusters(results_df, topic_mapping)
    
    # Print clusters in readable format
    pipeline.print_clusters(clusters)
    
    # Save to JSON file
    output_file = pipeline.save_clusters_to_json(clusters)
    print(f"\nClusters saved to: {output_file}")

if __name__ == "__main__":
    example_usage()