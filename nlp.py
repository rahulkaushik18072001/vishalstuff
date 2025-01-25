import json
from transformers import pipeline

# Load the JSON file
with open('articles.json', 'r') as file:
    data = json.load(file)

# Load the question-answering pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Iterate over each article and process the context
for article in data:
    # Combine 'description' and 'full_text' for context
    context = f"{article['description']} {article['full_text']}"
    
    print(f"\nTitle: {article['title']}")
    print(f"Link: {article['link']}")

    # Example questions for each article
    questions = [
        "What is the main topic of the article?",
        "What are the key details mentioned?",
        "Who is involved in the events described?",
        "When did the events take place?"
    ]

    # Answer each question
    for question in questions:
        result = qa_pipeline({'context': context, 'question': question})
        print(f"Q: {question}\nA: {result['answer']}")
