from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
import textwrap

class TextSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        """
        Initialize the summarizer with a specified model.
        Default is BART, which is good for news article summarization.
        """
        self.summarizer = pipeline("summarization", model=model_name)
        # Download necessary NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

    def chunk_text(self, text, max_chunk_size=1024):
        """
        Split text into smaller chunks that won't exceed the model's token limit.
        Uses sentence tokenization to avoid cutting sentences in the middle.
        """
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            if current_size + sentence_size <= max_chunk_size:
                current_chunk.append(sentence)
                current_size += sentence_size
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def summarize(self, text, max_length=60, min_length=50):
        """
        Summarize the input text.
        
        Args:
            text (str): Input text to summarize
            max_length (int): Maximum length of the summary in words
            min_length (int): Minimum length of the summary in words
            
        Returns:
            str: Generated summary
        """
        # Split text into chunks if it's too long
        chunks = self.chunk_text(text)
        summaries = []
        
        for chunk in chunks:
            summary = self.summarizer(chunk, 
                                    max_length=max_length, 
                                    min_length=min_length, 
                                    do_sample=False)
            summaries.append(summary[0]['summary_text'])
        
        # Combine all summaries
        final_summary = ' '.join(summaries)
        
        # Clean up the summary by wrapping text
        wrapped_summary = textwrap.fill(final_summary, width=80)
        return wrapped_summary

def main():
    with open('cleaned_text123.txt', 'r') as file:
    # Read the entire content of the file and store it in a variable
        sample_text = file.read()
    
    # Initialize summarizer
        summarizer = TextSummarizer()
    
    # Generate summary
        summary = summarizer.summarize(
        sample_text,
        max_length=150,  # Adjust these parameters based on your needs
        min_length=50
    )
    
    print("Original text length:", len(sample_text.split()))
    print("\nSummary:")
    print(summary)
    print("\nSummary length:", len(summary.split()))

if __name__ == "__main__":
    main()