import random
from utils.isl_converter import convert_to_isl

# Sample English sentences for quizzes
SAMPLE_SENTENCES = {
    'easy': [
        "My name is John",
        "I am happy",
        "She is a teacher",
        "He went to school",
        "Keep a safe distance",
        "I will call you tomorrow",
        "They work from home",
        "Can you help me",
        "Do not touch this",
        "The class is over"
    ],
    'medium': [
        "Yesterday I watched a beautiful movie",
        "My brother will graduate from college next month",
        "Can you tell me where the bathroom is",
        "I have been studying sign language for two years",
        "She doesn't want to go to the party tonight",
        "The red car belongs to my father",
        "We should finish our homework before playing",
        "Please sign your name on the dotted line",
        "How many languages do you speak fluently",
        "The children are playing in the garden"
    ],
    'hard': [
        "If it rains tomorrow, the outdoor event will be canceled",
        "After finishing her degree, she plans to work abroad for experience",
        "Can you explain why this algorithm is more efficient than the previous one",
        "Despite the challenges, they managed to complete the project on time",
        "The professor who taught us last semester has published a new book",
        "You should submit your application before the deadline expires next week",
        "When was the last time you visited your grandparents in their village",
        "The company announced that they will be hiring twenty new employees soon",
        "Please make sure that all electronic devices are turned off during the exam",
        "How many hours do you typically spend on learning new skills every day"
    ]
}

def generate_quiz(difficulty='easy', focus_areas=None, num_questions=5):
    """
    Generate a quiz with different question types
    
    Parameters:
    difficulty (str): 'easy', 'medium', or 'hard'
    focus_areas (list): List of specific areas to focus on (e.g., ['negation', 'questions'])
    num_questions (int): Number of questions to generate
    
    Returns:
    dict: Quiz data structure with questions and answers
    """
    if difficulty not in SAMPLE_SENTENCES:
        difficulty = 'easy'
    
    # Select sentences for this quiz
    available_sentences = SAMPLE_SENTENCES[difficulty]
    selected_sentences = random.sample(available_sentences, min(num_questions, len(available_sentences)))
    
    quiz = {
        'difficulty': difficulty,
        'questions': []
    }
    
    question_types = ['reordering', 'multiple_choice', 'fill_blanks']
    
    for i, sentence in enumerate(selected_sentences):
        # Convert to ISL
        isl_sentence = convert_to_isl(sentence)
        isl_words = isl_sentence.split()
        
        # Alternate question types
        question_type = question_types[i % len(question_types)]
        
        if question_type == 'reordering':
            # Create a reordering question
            shuffled_words = isl_words.copy()
            while shuffled_words == isl_words:  # Make sure it's actually shuffled
                random.shuffle(shuffled_words)
            
            question = {
                'id': f'q{i+1}',
                'type': 'reordering',
                'english': sentence,
                'shuffled_words': shuffled_words,
                'correct_order': isl_words
            }
            
        elif question_type == 'multiple_choice':
            # Create a multiple choice question about sentence structure
            options = []
            
            # Correct option
            options.append(isl_sentence)
            
            # Generate incorrect options by altering word order
            for _ in range(3):
                wrong_order = isl_words.copy()
                random.shuffle(wrong_order)
                wrong_sentence = " ".join(wrong_order)
                
                if wrong_sentence not in options:
                    options.append(wrong_sentence)
            
            # If we couldn't generate enough unique options, add more
            while len(options) < 4:
                # Add an option with an extra word
                extra_words = ["always", "sometimes", "maybe", "really", "very", "soon"]
                wrong_order = isl_words.copy()
                wrong_order.insert(random.randint(0, len(wrong_order)), random.choice(extra_words))
                wrong_sentence = " ".join(wrong_order)
                
                if wrong_sentence not in options:
                    options.append(wrong_sentence)
            
            random.shuffle(options)
            
            question = {
                'id': f'q{i+1}',
                'type': 'multiple_choice',
                'english': sentence,
                'question': 'Which is the correct ISL structure for this sentence?',
                'options': options,
                'correct_answer': options.index(isl_sentence)
            }
            
        elif question_type == 'fill_blanks':
            # Create a fill-in-the-blanks question
            blanked_words = isl_words.copy()
            
            # Determine how many blanks (1 or 2 depending on sentence length)
            num_blanks = 2 if len(blanked_words) >= 4 else 1
            blank_positions = random.sample(range(len(blanked_words)), num_blanks)
            
            blanks = {}
            for pos in blank_positions:
                blanks[pos] = blanked_words[pos]
                blanked_words[pos] = '_____'
            
            question = {
                'id': f'q{i+1}',
                'type': 'fill_blanks',
                'english': sentence,
                'sentence_with_blanks': " ".join(blanked_words),
                'blanks': blanks,
                'options': list(blanks.values())  # Provide the correct words as options
            }
            
        quiz['questions'].append(question)
    
    return quiz

def evaluate_quiz(quiz, user_answers):
    """
    Evaluate user answers for a quiz
    
    Parameters:
    quiz (dict): Quiz structure
    user_answers (dict): User's answers keyed by question id
    
    Returns:
    dict: Results with score and feedback
    """
    results = {
        'total_questions': len(quiz['questions']),
        'correct_answers': 0,
        'score_percentage': 0,
        'question_results': {},
        'weak_areas': [],
        'next_difficulty': quiz['difficulty']
    }
    
    for question in quiz['questions']:
        q_id = question['id']
        if q_id not in user_answers:
            results['question_results'][q_id] = {
                'correct': False,
                'feedback': 'No answer provided'
            }
            continue
            
        user_answer = user_answers[q_id]
        
        if question['type'] == 'reordering':
            correct = user_answer == question['correct_order']
            feedback = 'Correct!' if correct else f"The correct order is: {' '.join(question['correct_order'])}"
            
        elif question['type'] == 'multiple_choice':
            try:
                selected_index = int(user_answer)
                correct = selected_index == question['correct_answer']
                correct_option = question['options'][question['correct_answer']]
                feedback = 'Correct!' if correct else f"The correct answer is: {correct_option}"
            except (ValueError, IndexError):
                correct = False
                feedback = 'Invalid answer'
                
        elif question['type'] == 'fill_blanks':
            # Check if all blanks are filled correctly
            all_correct = True
            
            for pos, correct_word in question['blanks'].items():
                if str(pos) not in user_answer or user_answer[str(pos)] != correct_word:
                    all_correct = False
                    break
                    
            correct = all_correct
            
            if correct:
                feedback = 'Correct!'
            else:
                correct_sentence = " ".join(question['correct_order'] if 'correct_order' in question else question['sentence_with_blanks'].replace('_____', '[answer]'))
                feedback = f"The correct sentence is: {correct_sentence}"
        
        results['question_results'][q_id] = {
            'correct': correct,
            'feedback': feedback
        }
        
        if correct:
            results['correct_answers'] += 1
        else:
            # Track areas of weakness based on question type
            results['weak_areas'].append(question['type'])
    
    # Calculate score percentage
    if results['total_questions'] > 0:
        results['score_percentage'] = (results['correct_answers'] / results['total_questions']) * 100
    
    # Determine next difficulty level
    if results['score_percentage'] >= 80:
        if quiz['difficulty'] == 'easy':
            results['next_difficulty'] = 'medium'
        elif quiz['difficulty'] == 'medium':
            results['next_difficulty'] = 'hard'
    elif results['score_percentage'] < 50:
        if quiz['difficulty'] == 'hard':
            results['next_difficulty'] = 'medium'
        elif quiz['difficulty'] == 'medium':
            results['next_difficulty'] = 'easy'
    
    # Count occurrences of each weak area
    from collections import Counter
    weak_area_counts = Counter(results['weak_areas'])
    
    # Only keep the most frequent weak areas
    results['weak_areas'] = [area for area, count in weak_area_counts.most_common(2)]
    
    return results