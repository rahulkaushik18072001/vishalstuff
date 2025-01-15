import nltk
from transformers import pipeline

# Download the necessary NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')

def split_into_paragraphs(text):
    return text.split('\n\n')

def split_into_chunks(text, max_length=1024):
    sentences = nltk.tokenize.sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(nltk.tokenize.word_tokenize(sentence))
        if current_length + sentence_length <= max_length:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def summarize_text(text, summarizer):
    try:
        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return text  # Return the original text if an error occurs

def main():
    # Initialize the summarizer
    summarizer = pipeline("summarization")

    # Read the long text from a file
    with open('long_text.txt', 'r') as file:
        long_text = file.read()

    # Split the text into paragraphs
    paragraphs = split_into_paragraphs(long_text)

    # Split paragraphs into smaller chunks
    chunks = []
    for paragraph in paragraphs:
        chunks.extend(split_into_chunks(paragraph))

    # Summarize each chunk
    summarized_chunks = [summarize_text(chunk, summarizer) for chunk in chunks]

    # Combine the summarized chunks
    summarized_text = '\n\n'.join(summarized_chunks)

    # Write the summarized text to a file
    with open('summarized_text.txt', 'w') as file:
        file.write(summarized_text)

if __name__ == "__main__":
    main()