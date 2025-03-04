import spacy
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import ssl
import nltk

# SSL certificate handling for NLTK downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load NLP components
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

def convert_to_isl(sentence):
    """
    Convert English sentence to Indian Sign Language (ISL) structure
    """
    # Process the sentence with spaCy
    doc = nlp(sentence)
    
    # Detect tense
    tense_markers = {
        "future": ["will", "shall", "going to"],
        "past": ["was", "were", "had", "did"],
        "present_continuous": ["am", "is", "are"],
    }
    
    tense = None
    for token in doc:
        if token.text.lower() in tense_markers["future"] or token.tag_ == "MD":
            tense = "future"
            break
        elif token.text.lower() in tense_markers["past"] or token.tag_ in ["VBD", "VBN"]:
            tense = "past"
            break
        elif token.text.lower() in tense_markers["present_continuous"] and any(t.tag_ == "VBG" for t in doc):
            tense = "present_continuous"
            break
    
    # Handle negations
    negation_words = {"not", "no", "never", "don't", "doesn't", "isn't", "won't", "didn't", "can't", "shouldn't"}
    negation_expressions = {"do not", "does not", "is not", "will not", "did not", "cannot", "should not"}
    
    negation_flag = False
    for neg_expr in negation_expressions:
        if neg_expr in sentence.lower():
            negation_flag = True
            break
    
    if not negation_flag:
        for token in doc:
            if token.text.lower() in negation_words:
                negation_flag = True
                break
    
    # Extract components for ISL structure
    subjects = []
    objects = []
    verbs = []
    adjectives = {}  # Map nouns to their adjectives
    adverbs = []
    time_expressions = []
    question_words = []
    possessives = {}  # Map nouns to their possessors
    numbers = {}      # Map nouns to their numerical values
    
    # First pass to identify subjects, possessives, and numbers
    for token in doc:
        # Store question words
        if token.tag_ in ["WDT", "WP", "WP$", "WRB"]:
            question_words.append(token.text.lower())
        
        # Store time expressions
        if token.dep_ == "npadvmod" and token.pos_ == "NOUN":
            time_expressions.append(token.text.lower())
            
        # Handle possessive pronouns (my, your, etc.)
        if token.tag_ == "PRP$":
            if token.head.lemma_ not in possessives:
                possessives[token.head.lemma_] = token.text.lower()
                
        # Store numbers associated with nouns
        if token.pos_ == "NUM":
            # Find the noun this number modifies or relates to
            if token.head.pos_ == "NOUN":
                numbers[token.head.lemma_] = token.text
            # Handle predicative numbers (age is 22)
            elif token.dep_ == "attr" or token.dep_ == "acomp":
                for t in doc:
                    if t.pos_ == "NOUN" and t.dep_ == "nsubj":
                        numbers[t.lemma_] = token.text
                        break
    
    # Build adjective mapping
    for token in doc:
        if token.pos_ == "ADJ":
            # Find the noun this adjective modifies
            if token.head.pos_ == "NOUN":
                if token.head.lemma_ not in adjectives:
                    adjectives[token.head.lemma_] = []
                adjectives[token.head.lemma_].append(token.text.lower())
    
    # Extract main components
    for token in doc:
        # Skip articles and auxiliary verbs
        if token.text.lower() in {"a", "an", "the", "is", "are", "am", "was", "were", "be", "to"}:
            continue
            
        # Skip negation words as we handle them separately
        if token.text.lower() in negation_words:
            continue
            
        # Handle subjects, objects, and verbs
        if token.dep_ in ["nsubj", "nsubjpass"] and token.pos_ in ["NOUN", "PROPN", "PRON"]:
            # Convert "I" to "Me" for ISL
            word = "Me" if token.text.lower() == "i" else token.text
            subjects.append(word.lower())
        elif token.dep_ in ["dobj", "pobj", "attr"] and token.pos_ in ["NOUN", "PROPN", "PRON"]:
            objects.append(token.lemma_.lower())
        elif token.pos_ == "VERB" and token.dep_ not in ["aux", "auxpass"]:
            # Get the base form of the verb
            verbs.append(token.lemma_.lower())
        elif token.pos_ == "ADV" and token.dep_ != "advmod":
            adverbs.append(token.text.lower())
    
    # Special case: Handle imperative sentences (commands) like "Keep a safe distance"
    is_imperative = False
    if len(subjects) == 0 and len(verbs) > 0 and doc[0].pos_ == "VERB":
        is_imperative = True
    
    # Build the ISL sentence
    isl_parts = []
    
    # Start with question words if any
    if question_words:
        isl_parts.extend(question_words)
    
    # Add time markers
    if tense == "past":
        isl_parts.append("Before")
    elif tense == "future":
        isl_parts.append("Will")
    elif tense == "present_continuous":
        isl_parts.append("Now")
    
    # Add time expressions if any
    isl_parts.extend(time_expressions)
    
    # Add negation if needed
    if negation_flag:
        isl_parts.append("No")
    
    if is_imperative:
        # For imperatives: VERB + ADJECTIVE + NOUN (keep safe distance)
        isl_parts.extend(verbs)
        
        # Add adjectives followed by their nouns
        for obj in objects:
            obj_with_adj = []
            
            # Add possessive if exists
            if obj in possessives:
                obj_with_adj.append(possessives[obj])
                
            # Add adjectives
            if obj in adjectives:
                obj_with_adj.extend(adjectives[obj])
                
            obj_with_adj.append(obj)
            
            # Add number if exists
            if obj in numbers:
                obj_with_adj.append(numbers[obj])
                
            isl_parts.extend(obj_with_adj)
        
        # Add adverbs
        isl_parts.extend(adverbs)
    else:
        # For non-imperatives: follow SOV structure
        # Add subjects with their adjectives
        for subject in subjects:
            subj_with_adj = []
            
            # Add possessive if exists
            if subject in possessives:
                subj_with_adj.append(possessives[subject])
                
            # Add adjectives
            if subject in adjectives:
                subj_with_adj.extend(adjectives[subject])
                
            subj_with_adj.append(subject)
            
            # Add number if exists
            if subject in numbers:
                subj_with_adj.append(numbers[subject])
                
            isl_parts.extend(subj_with_adj)
        
        # Add objects with their adjectives
        for obj in objects:
            obj_with_adj = []
            
            # Add possessive if exists
            if obj in possessives:
                obj_with_adj.append(possessives[obj])
                
            # Add adjectives
            if obj in adjectives:
                obj_with_adj.extend(adjectives[obj])
                
            obj_with_adj.append(obj)
            
            # Add number if exists
            if obj in numbers:
                obj_with_adj.append(numbers[obj])
                
            isl_parts.extend(obj_with_adj)
        
        # Add adverbs
        isl_parts.extend(adverbs)
        
        # Add verbs
        isl_parts.extend(verbs)
    
    # Special case for state/identity sentences
    is_identity_sentence = False
    for token in doc:
        if token.lemma_ == "be" and any(t.dep_ == "attr" for t in doc):
            is_identity_sentence = True
            break
            
    # Ensure that sentences like "My age is 22" retain the number
    if is_identity_sentence and len(subjects) > 0:
        for subject in subjects:
            if subject in numbers and numbers[subject] not in isl_parts:
                # Find where to insert the number (right after the subject)
                subject_index = isl_parts.index(subject) if subject in isl_parts else -1
                if subject_index != -1:
                    isl_parts.insert(subject_index + 1, numbers[subject])
    
    # Special case: if the sentence is just about states or feelings (like "I am thirsty")
    if "am" in sentence.lower() and len(subjects) > 0 and len(objects) == 0 and len(verbs) == 0:
        # Extract predicative adjectives
        for token in doc:
            if token.pos_ == "ADJ" and token.dep_ == "acomp":
                isl_parts.append(token.text.lower())
    
    # Remove duplicates while preserving order
    seen = set()
    isl_parts = [x for x in isl_parts if not (x in seen or seen.add(x))]
    
    # Create the final ISL sentence
    isl_sentence = " ".join(isl_parts).strip()
    
    # If empty output, handle various cases
    if not isl_sentence:
        # Try to construct a minimal sensible output
        if len(subjects) > 0 and any(s in numbers for s in subjects):
            # For identity sentences with numbers
            for s in subjects:
                if s in numbers:
                    isl_sentence = f"{s} {numbers[s]}"
                    break
        elif len(verbs) > 0:
            # Return at least the main verb
            isl_sentence = verbs[0]
        elif len(objects) > 0:
            # Return at least the main object
            isl_sentence = objects[0]
        elif len(subjects) > 0:
            # Return at least the main subject
            isl_sentence = subjects[0]
    
    return isl_sentence