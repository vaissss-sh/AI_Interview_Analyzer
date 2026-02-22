import re
from transformers import pipeline

class NLPAnalyzer:
    def __init__(self):
        # We assume models will be cached by Streamlit
        self.sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        self.emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
        
        self.filler_words = [r'\bum\b', r'\buh\b', r'\blah\b', r'\blike\b', r'\bbasically\b', r'\bactually\b', r'\bliterally\b']
        self.filler_regex = re.compile('|'.join(self.filler_words), re.IGNORECASE)

    def analyze(self, text):
        if not text.strip():
            return {
                "sentiment": "Neutral",
                "sentiment_score": 0.5,
                "emotion": "Neutral",
                "emotion_score": 0.5,
                "fillers_count": 0,
                "fillers_list": {}
            }
            
        # 1. Sentiment
        sentiment_res = self.sentiment_pipeline(text[:512])[0] # truncate to avoid max length error
        sentiment_label = sentiment_res['label']
        raw_score = sentiment_res['score']
        
        # normalized sentiment 0 to 1
        if sentiment_label == "POSITIVE":
            sentiment_score = 0.5 + (raw_score / 2.0)
        else:
            sentiment_score = 0.5 - (raw_score / 2.0)

        # 2. Emotion
        emotion_res = self.emotion_pipeline(text[:512])[0]
        emotion_label = emotion_res['label']
        emotion_score = emotion_res['score']

        # 3. Filler Words
        fillers = self.filler_regex.findall(text)
        fillers_lower = [f.lower() for f in fillers]
        
        filler_counts = {}
        for f in fillers_lower:
            filler_counts[f] = filler_counts.get(f, 0) + 1
            
        return {
            "sentiment": sentiment_label,
            "sentiment_score": sentiment_score,
            "emotion": emotion_label,
            "emotion_score": emotion_score,
            "fillers_count": len(fillers),
            "fillers_list": filler_counts
        }
