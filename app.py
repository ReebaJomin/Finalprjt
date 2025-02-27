
from flask import Flask, render_template, request, session, jsonify
from recommender import SignLingoRandomForestRecommender
from recommender2 import SignLingoRandomForestRecommender
import pandas as pd
import sqlite3
import os
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "supersecretkey"  # Change this for security
Session(app)

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    progress_level = db.Column(db.Integer, default=1)

# Create database tables (Run once)
with app.app_context():
    db.create_all()

# User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    gender = data.get("gender")

    user = User.query.filter_by(username=username, gender=gender).first()
    if user:
        session["user_id"] = user.id
        return jsonify({"message": "Login successful", "user_id": user.id})
    return jsonify({"message": "Invalid credentials"}), 401

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"})

# Get current user
@app.route("/get_current_user", methods=["GET"])
def get_current_user():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            return jsonify({"user_id": user.id, "progress_level": user.progress_level})
    return jsonify({"message": "Not logged in"}), 401

# Update user progress
@app.route("/update_progress", methods=["POST"])
def update_progress():
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401
    
    data = request.json
    user = User.query.get(session["user_id"])

    if user and data["progress_level"] > user.progress_level:
        user.progress_level = data["progress_level"]
        db.session.commit()
        return jsonify({"message": "Progress updated!"})
    
    return jsonify({"message": "No progress update needed"}), 400

# Get user progress
@app.route("/progress", methods=["GET"])
def get_progress():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            return jsonify({"progress_level": user.progress_level})
    return jsonify({"message": "Unauthorized"}), 401

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    gender = data.get("gender")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already taken"}), 400

    new_user = User(username=username, gender=gender)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Signup successful!"})

df = pd.read_csv(r"C:\Users\DELL\OneDrive\Desktop\Final_prjt\Final_dataset.csv")
# Initialize sample data and recommender
sample_data=pd.read_csv("filtered_categories.csv")
data=pd.read_csv("learning.csv")
#data=pd.read_csv("alphabet.csv")
recommender = SignLingoRandomForestRecommender(sample_data)
recommender2 = SignLingoRandomForestRecommender(data)

@app.route('/')
def web():
    return render_template('web.html')
# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get("name")
    gender = data.get("gender")

    if not name or not gender:
        return jsonify({"error": "Missing name or gender"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, gender) VALUES (?, ?)", (name, gender))
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully!"}), 201


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
        
        words = word_tokenize(sentence)
        pos_tags = pos_tag(words)
        
        
        verb_index = next((i for i, word_pos in enumerate(pos_tags) if word_pos[1].startswith('VB')), None)
        
        if verb_index is not None:
            # Identify subject, verb, and object
            subject = " ".join(words[:verb_index])  
            verb = words[verb_index]  
            object_words = words[verb_index + 1:]
            
            
            object_phrase = " ".join(object_words)
            isl_sentence = f"{subject.strip()} {object_phrase.strip()} {verb.strip()}".strip()
            
            
            isl_sentence = re.sub(r'\s([?.!,"](?:\s|$))', r'\1', isl_sentence)
            isl_sentences.append(isl_sentence)
        else:
            
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

@app.route('/roadmap.html')
def roadmap():
    return render_template('roadmap.html')

@app.route('/temp.html')
def temp():
    return render_template('temp.html')

@app.route('/temp2.html')
def temp2():
    return render_template('temp2.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/index2.html')
def index2():
    return render_template('index2.html')

@app.route('/sign.html')
def sign():
    return render_template('sign.html')

@app.route('/game.html')
def game():
    return render_template('game.html')

@app.route('/quiz.html')
def quiz():
    return render_template('quiz.html')

@app.route('/number.html')
def number():
    return render_template('number.html')

@app.route('/learn', methods=['POST'])
def learn():
    word = request.form.get('word', '').lower().strip()
    
    if not word:
        return jsonify({'error': 'Please enter a word'})
    
    try:
        recommendations = recommender2.recommend(word, top_n=5)
        # Convert to dictionary for JSON response
        results = recommendations.to_dict('records')
        return jsonify({'recommendations': results})
    except Exception as e:
        return jsonify({'error': f'Error getting recommendations: {str(e)}'})
    
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