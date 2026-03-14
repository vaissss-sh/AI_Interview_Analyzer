import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
import re

# We use the small english model for faster loading. You must run: python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spacy model 'en_core_web_sm' not found. It will need to be downloaded.")
    nlp = None

analyzer = SentimentIntensityAnalyzer()

def analyze_answer(text: str, question: str) -> dict:
    """
    Analyzes an answer text based on relevance, grammar, vocab, sentiment, completeness.
    """
    if not text:
        return {
            "relevance_score": 0.0,
            "grammar_score": 0.0,
            "vocabulary_score": 0.0,
            "sentiment": 0.0,
            "completeness": 0.0,
            "key_points_covered": []
        }
        
    doc = nlp(text) if nlp else None
    
    # Simple Word Count + Structure for completeness
    word_count = len(text.split())
    completeness = min(100.0, (word_count / 150.0) * 100) # Assuming 150 words is a fully complete answer
    
    # Sentiment
    sentiment_dict = analyzer.polarity_scores(text)
    sentiment = (sentiment_dict['compound'] + 1) * 50 # Normalize -1..1 to 0..100
    
    # Vocab score logic
    vocab_level = get_vocabulary_level(text)
    vocab_scores = {"basic": 50, "intermediate": 75, "advanced": 95}
    vocabulary_score = vocab_scores.get(vocab_level, 50)
    
    # Key topics
    key_points = extract_key_topics(text)
    
    return {
        "relevance_score": min(100.0, len(key_points) * 15 + 40), # Dummy heuristic
        "grammar_score": 85.0, # Placeholder for grammar checking API/model
        "vocabulary_score": vocabulary_score,
        "sentiment": round(sentiment, 2),
        "completeness": round(completeness, 2),
        "key_points_covered": key_points[:5]
    }

def get_vocabulary_level(text: str) -> str:
    """Classifies vocabulary complexity based on unique word ratio and average word length."""
    words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
    if not words: return "basic"
    
    unique_ratio = len(set(words)) / len(words)
    avg_length = sum(len(w) for w in words) / len(words)
    
    if avg_length > 6.5 and unique_ratio > 0.6:
        return "advanced"
    elif avg_length > 5.0 and unique_ratio > 0.4:
        return "intermediate"
    else:
        return "basic"

def extract_key_topics(text: str) -> list:
    """Extracts noun chunks and named entities as key topics."""
    if not nlp: return []
    doc = nlp(text)
    
    topics = []
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART", "GPE"]:
            topics.append(ent.text)
            
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1 and chunk.text.lower() not in [t.lower() for t in topics]:
            topics.append(chunk.text)
            
    # Filter common stop words from single word topics
    topics = list(set([t.lower() for t in topics if len(t) > 2]))
    return topics

def generate_word_cloud_data(transcripts: list) -> dict:
    """Compiles all text and returns word frequencies for a word cloud."""
    full_text = " ".join(transcripts).lower()
    words = re.findall(r'\b[a-z]{4,}\b', full_text) # Only words 4+ chars
    
    # Simple stop word filter
    stop_words = {'that', 'this', 'with', 'from', 'your', 'have', 'more', 'about'}
    words = [w for w in words if w not in stop_words]
    
    return dict(Counter(words).most_common(50))

def get_answer_sentiment_arc(transcripts_list: list) -> list:
    """Returns a list of sentiment scores for each answer sequentially."""
    arc = []
    for t in transcripts_list:
        if not t:
            arc.append(50.0) # neutral default
        else:
            s_dict = analyzer.polarity_scores(t)
            arc.append(round((s_dict['compound'] + 1) * 50, 2))
    return arc
