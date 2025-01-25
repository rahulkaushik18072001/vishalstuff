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
        """
        Process and cluster news articles.
        
        Args:
            articles: List of dictionaries containing article info with 'title' and 'content' keys
            
        Returns:
            DataFrame with clustering results and topic information
        """
        # Combine title and content for better context
        texts = [f"{art['title']}. {art['content']}" for art in articles]
        
        # Fit the topic model and transform the documents
        topics, probs = self.topic_model.fit_transform(texts)
        
        # Get topic info and representative terms
        topic_info = self.topic_model.get_topic_info()
        
        # Create results DataFrame
        results_df = pd.DataFrame({
            'title': [art['title'] for art in articles],
            'content': [art['content'] for art in articles],
            'topic_id': topics,
            'confidence': probs.max(axis=1) if len(probs.shape) > 1 else probs
        })
        
        # Create topic mapping
        topic_mapping = {}
        for topic_id in results_df['topic_id'].unique():
            if topic_id != -1:  # -1 is reserved for outliers
                topic_terms = self.topic_model.get_topic(topic_id)
                topic_mapping[topic_id] = [term[0] for term in topic_terms[:5]]
        
        return results_df, topic_mapping
    
    def get_similar_articles(self, 
                           target_article: Dict,
                           articles: List[Dict],
                           threshold: float = 0.7) -> List[Dict]:
        """
        Find similar articles to a target article using semantic similarity.
        
        Args:
            target_article: Dictionary containing target article info
            articles: List of articles to compare against
            threshold: Similarity threshold for matching
            
        Returns:
            List of similar articles
        """
        target_text = f"{target_article['title']}. {target_article['content']}"
        compare_texts = [f"{art['title']}. {art['content']}" for art in articles]
        
        # Generate embeddings
        target_embedding = self.encoder.encode(target_text)
        article_embeddings = self.encoder.encode(compare_texts)
        
        # Calculate similarities
        similarities = np.dot(article_embeddings, target_embedding) / (
            np.linalg.norm(article_embeddings, axis=1) * np.linalg.norm(target_embedding)
        )
        
        # Get similar articles above threshold
        similar_indices = np.where(similarities > threshold)[0]
        similar_articles = [
            {**articles[i], 'similarity_score': similarities[i]} 
            for i in similar_indices
        ]
        
        return sorted(similar_articles, key=lambda x: x['similarity_score'], reverse=True)

def example_usage():
    # Sample articles
    with open ('articles.json') as f:
        articles = json.load(f)
    
    # Initialize pipeline
    pipeline = NewsClusteringPipeline()
    
    # Process articles
    results_df, topic_mapping = pipeline.process_articles(articles)
    
    # Print results
    print("\nClustering Results:")
    print(results_df[['title', 'topic_id', 'confidence']])
    print("\nTopic Keywords:")
    for topic_id, keywords in topic_mapping.items():
        print(f"Topic {topic_id}: {', '.join(keywords)}")

if __name__ == "__main__":
    example_usage()