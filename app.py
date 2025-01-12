
from flask import Flask, render_template, request, jsonify
from recommender import SignLingoRandomForestRecommender
import pandas as pd
import os

app = Flask(__name__)

df = pd.read_csv(r"C:\Users\DELL\OneDrive\Desktop\Final_prjt\Final_dataset.csv")
# Initialize sample data and recommender
sample_data=pd.read_csv("filtered_categories.csv")

recommender = SignLingoRandomForestRecommender(sample_data)

def convert_to_isl_structure(paragraph):
    # Split the paragraph into sentences
    import re
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk import pos_tag

    # Ensure necessary NLTK data is downloaded
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
    isl_sentences = []
    
    for sentence in sentences:
        # Tokenize and POS tag the sentence
        words = word_tokenize(sentence)
        pos_tags = pos_tag(words)
        
        # Find the first verb in the sentence
        verb_index = next((i for i, word_pos in enumerate(pos_tags) if word_pos[1].startswith('VB')), None)
        
        if verb_index is not None:
            # Identify subject, verb, and object
            subject = " ".join(words[:verb_index])  # Words before the verb
            verb = words[verb_index]  # The verb itself
            object_words = words[verb_index + 1:]  # Words after the verb
            
            # Rearrange into Subject-Object-Verb (SOV)
            object_phrase = " ".join(object_words)
            isl_sentence = f"{subject.strip()} {object_phrase.strip()} {verb.strip()}".strip()
            
            # Fix spacing around punctuation
            isl_sentence = re.sub(r'\s([?.!,"](?:\s|$))', r'\1', isl_sentence)
            isl_sentences.append(isl_sentence)
        else:
            # If no verb is found, keep the original sentence
            isl_sentences.append(sentence.strip())
    
    # Join the ISL sentences back into a paragraph
    return " ".join(isl_sentences)

def preprocess_text(text):
    import nltk
    import string
    from nltk.tokenize import word_tokenize
    from nltk.stem.wordnet import WordNetLemmatizer
    lemma = WordNetLemmatizer()
    text = text.lower()
    text = "".join([char for char in text if char not in string.punctuation])
    words = word_tokenize(text)
    lemmatized_words = [lemma.lemmatize(word) for word in words]
    return " ".join(lemmatized_words)

@app.route('/')
def web():
    return render_template('web.html')

@app.route('/roadmap.html')
def roadmap():
    return render_template('roadmap.html')

@app.route('/temp.html')
def temp():
    return render_template('temp.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/sign.html')
def sign():
    return render_template('sign.html')

@app.route('/game.html')
def game():
    return render_template('game.html')

@app.route('/search', methods=['POST'])
def search():
    word = request.form.get('word', '').lower().strip()
    
    if not word:
        return jsonify({'error': 'Please enter a word'})
    
    try:
        recommendations = recommender.recommend(word, top_n=5)
        # Convert to dictionary for JSON response
        results = recommendations.to_dict('records')
        return jsonify({'recommendations': results})
    except Exception as e:
        return jsonify({'error': f'Error getting recommendations: {str(e)}'})

@app.route('/get_videos', methods=['POST'])
def get_videos():
    # Use predefined paragraph
    data = request.get_json()
    user_paragraph = data.get('paragraph', '')

    isl_paragraph = convert_to_isl_structure(user_paragraph)
    cleaned_summarized_text = preprocess_text(isl_paragraph)
    # Find matching words and their corresponding URLs
    words = cleaned_summarized_text.split()
    video_urls = []
    for word in words:
        match = df[df['word'].str.lower() == word.lower()]
        if not match.empty:
            video_urls.append(match.iloc[0]['url'])
        else:
            continue    

    return jsonify(video_urls=video_urls)


if __name__ == '__main__':
    app.run(debug=True)