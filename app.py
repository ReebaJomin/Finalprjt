from flask import Flask, render_template, request, session, jsonify
from utils.isl_converter import convert_to_isl
from utils.quiz_generator import generate_quiz, evaluate_quiz
from utils.user_progress import update_user_progress, get_user_stats
from recommender import SignLingoRandomForestRecommender
from recommender2 import SignLingoRandomForestRecommender
import pandas as pd
import sqlite3
import os
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import nltk
nltk.download('wordnet')

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
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
    date = db.Column(db.String(20), nullable=False,default=lambda: datetime.now().strftime("%Y-%m-%d"))
    progress_level = db.Column(db.Integer, default=1,nullable=False)
    noquiz=db.Column(db.Integer, default=1,nullable=False)
    alphaquiz=db.Column(db.Integer, default=1,nullable=False)

# Create database tables (Run once)
with app.app_context():
    #db.drop_all()  # Delete all tables
    db.create_all()  # Recreate tables with the new structure
    print("Database tables recreated!")

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
            return jsonify({"user_id": user.id,"username": user.username, "gender":user.gender,"date":user.date,"progress_level": user.progress_level,"noquiz":user.noquiz,"alphaquiz":user.alphaquiz})
    return jsonify({"message": "Not logged in"}), 401

# Update user progress
'''@app.route("/update_progress", methods=["POST"])
def update_progress():
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401
    
    data = request.json
    user = User.query.get(session["user_id"])
    user.date=data["date"]
    if user and data["progress_level"] > user.progress_level:
        user.progress_level = data["progress_level"]
        db.session.commit()
        return jsonify({"message": "Progress updated!"})
    
    return jsonify({"message": "No progress update needed"}), 400
'''
@app.route('/update_progress', methods=['POST'])
def update_progress():
    data = request.json
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.date=data["date"]
        user.progress_level = data.get("progress_level", user.progress_level)
        user.alphaquiz = data.get("alphaquiz", user.alphaquiz)
        user.noquiz = data.get("noquiz", user.noquiz)
        db.session.commit()
        return jsonify({"message": "Progress updated successfully"})
    
    return jsonify({"error": "User not found"}), 404

# Get user progress

@app.route('/progress', methods=['GET'])
def get_progress():
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    
    user = User.query.filter_by(id=user_id).first()
    
    if user:
        return jsonify({
            "date": user.date,
            "progress_level": user.progress_level,
            "noquiz": user.noquiz,
            "alphaquiz":user.alphaquiz
        })
    
    return jsonify({"error": "User not found"}), 404

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
'''def get_db_connection():
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
'''

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
    import string
    from nltk.tokenize import word_tokenize
    from nltk.stem.wordnet import WordNetLemmatizer
    lemma = WordNetLemmatizer()
    text = text.lower()
    text = "".join([char for char in text if char not in string.punctuation])
    words = word_tokenize(text)
    lemmatized_words = [lemma.lemmatize(word) for word in words]
    return " ".join(lemmatized_words)

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')
@app.route('/roadmap.html')
def roadmap():
    return render_template('roadmap.html')

@app.route('/temp.html')
def temp():
    return render_template('temp.html')

@app.route('/temp2.html')
def temp2():
    return render_template('temp2.html')

@app.route('/temp3.html')
def temp3():
    return render_template('temp3.html')

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

@app.route('/quiz1.html')
def quiz1():
    return render_template('quiz1.html')

@app.route('/word1.html')
def word():
    return render_template('word1.html')

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

@app.route('/index3.html')
def index3():
    return render_template('index3.html')
@app.route('/quiz3.html')
def quiz3():
    return render_template('quiz3.html')

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    sentence = data.get("sentence", "")
    isl_sentence = convert_to_isl(sentence)
    
    # Get the list of available videos
    video_words = get_available_videos()
    
    # Check which words have corresponding videos
    words_with_videos = []
    for word in isl_sentence.split():
        if word.lower() in [v.lower() for v in video_words]:
            words_with_videos.append({"word": word, "hasVideo": True})
        else:
            words_with_videos.append({"word": word, "hasVideo": False})
    
    return jsonify({
        "isl_sentence": isl_sentence,
        "words_with_videos": words_with_videos
    })

@app.route("/quiz")
def quiz():
    if 'current_quiz' not in session:
        session['current_quiz'] = generate_quiz(difficulty='easy')

    print(session['current_quiz'])  # Debugging line

    return render_template("quiz3.html", quiz=session.get('current_quiz', {}))

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    data = request.get_json()
    user_answers = data.get("answers", {})
    
    # Evaluate the quiz results
    results = evaluate_quiz(session['current_quiz'], user_answers)
    
    # Update user progress
    if 'user_id' in session:
        update_user_progress(session['user_id'], results)
    
    # Generate a new quiz for next time
    session['current_quiz'] = generate_quiz(
        difficulty=results['next_difficulty'],
        focus_areas=results['weak_areas']
    )
    
    return jsonify(results)

@app.route("/play_video/<word>")
def play_video(word):
    # Return the video path for the requested word
    video_path = f"/static/assets/videos/{word.lower()}.mp4"
    return jsonify({"path": video_path})

def get_available_videos():
    # Get the list of available video files (without extension)
    video_dir = os.path.join(app.static_folder, "assets", "videos")
    if os.path.exists(video_dir):
        return [os.path.splitext(f)[0] for f in os.listdir(video_dir) if f.endswith('.mp4')]
    return []

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)