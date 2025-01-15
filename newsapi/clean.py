import json

def clean_text(text):
    # Your cleaning logic here
    return text.strip()

# Read the JSON file
with open('articles.json', 'r') as json_file:
    data = json.load(json_file)

cleaned_texts = []

# Extract and clean all "content" fields
for article in data:
    if 'content' in article:
        raw_text = article['content']
        cleaned_text = clean_text(raw_text)
        cleaned_texts.append(cleaned_text)

# Write the cleaned texts to a JSON file
with open('cleaned_text.json', 'w') as file:
    json.dump(cleaned_texts, file, indent=4)

