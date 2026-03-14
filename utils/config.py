import os
from dotenv import load_dotenv

load_dotenv()

WHISPER_MODEL = "base"
DEEPFACE_MODEL = "Facenet"
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024

TEMP_DIR = os.getenv("TEMP_DIR", "temp/")
DB_PATH = os.getenv("DB_PATH", "data/sessions.db")
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "models/")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Scoring system weights mapped exactly to user specs
SCORING_WEIGHTS = {
    "communication": 0.20,
    "confidence": 0.20,
    "technical": 0.25,
    "emotional_iq": 0.15,
    "engagement": 0.10,
    "professionalism": 0.10
}

# Filler words for audio/NLP analysis
FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "literally"]

# Expected emotion labels from DeepFace
EMOTION_LABELS = ["happy", "sad", "angry", "fear", "surprise", "neutral", "disgust"]

# Ensure directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
