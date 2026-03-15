#!/bin/bash
set -e
echo "=== InterviewIQ Model Pre-download ==="

# Check if packages are installed, if not, install them first
# This ensures setup.sh works even if run before requirements.txt 
echo "Checking dependencies..."
python -c "import deepface" 2>/dev/null || pip install -r requirements.txt

echo "1. Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "2. Pre-caching Whisper tiny model..."
python -c "
import whisper
print('Downloading Whisper tiny...')
whisper.load_model('tiny')
print('Whisper ready!')
"

echo "3. Pre-warming DeepFace..."
python -c "
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    from deepface import DeepFace
    import numpy as np
    dummy = np.zeros((48,48,3), dtype=np.uint8)
    DeepFace.analyze(dummy, actions=['emotion'],
                    enforce_detection=False, silent=True)
    print('DeepFace ready!')
except Exception as e:
    print('DeepFace pre-warm Warning (non-fatal):', e)
"

echo "=== All models pre-downloaded successfully ==="
