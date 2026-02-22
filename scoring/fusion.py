def calculate_score(metrics):
    """
    metrics = {
        "wpm": float,
        "transcript_length": int, # words
        "fillers_count": int,
        "sentiment_score": float, # 0 to 1
        "emotion": str, 
        "pauses_seconds": float,
        "eye_contact_percentage": float, # 0 to 100
        "blink_count": int,
        "duration_minutes": float
    }
    """
    
    # Weights
    W_FILLER = 0.18
    W_WPM = 0.18
    W_SENTIMENT = 0.12
    W_EMOTION = 0.10
    W_PAUSES = 0.12
    W_EYE = 0.15
    W_BLINK = 0.15
    
    # 1. Filler Density 
    total_words = metrics.get('transcript_length', 1)
    if total_words == 0: total_words = 1
    
    filler_density = metrics.get('fillers_count', 0) / total_words
    # Assuming > 5% fillers is bad, 0% is perfect
    filler_score = max(0, 100 - (filler_density * 2000))
    filler_score = min(100, filler_score)
    
    # 2. WPM
    wpm = metrics.get('wpm', 0)
    if 130 <= wpm <= 160:
        wpm_score = 100
    elif wpm < 130:
        wpm_score = max(0, 100 - (130 - wpm) * 1.5)
    else:
        wpm_score = max(0, 100 - (wpm - 160) * 1.0)
        
    # 3. Sentiment (0 to 1 already)
    sentiment_score = metrics.get('sentiment_score', 0.5) * 100
    
    # 4. Emotion
    emotion = metrics.get('emotion', 'neutral').lower()
    good_emotions = ['joy', 'surprise', 'neutral', 'approval']
    bad_emotions = ['sadness', 'fear', 'anger', 'disgust']
    if emotion in good_emotions:
        emotion_score = 100
    elif emotion in bad_emotions:
        emotion_score = 40
    else:
        emotion_score = 70
        
    # 5. Pauses (seconds)
    duration_minutes = metrics.get('duration_minutes', 0.1)
    if duration_minutes <= 0: duration_minutes = 0.1
    pauses_per_min = metrics.get('pauses_seconds', 0) / duration_minutes
    # More than 10 seconds of hesitation pauses per minute is bad
    pause_score = max(0, 100 - (pauses_per_min * 10))
    
    # 6. Eye Contact (Percentage)
    eye_score = metrics.get('eye_contact_percentage', 0)
    
    # 7. Blink / Stress
    blink_count = metrics.get('blink_count', 0)
    bpm = blink_count / duration_minutes
    # Normal is 15-20. Under 10 or over 30 is stress/staring
    if 10 <= bpm <= 25:
        blink_score = 100
    else:
        deviation = min(abs(bpm - 17.5), 30)
        blink_score = max(0, 100 - (deviation * 3))
        
    # Calculate Final Score
    final_score = (
        (filler_score * W_FILLER) +
        (wpm_score * W_WPM) +
        (sentiment_score * W_SENTIMENT) +
        (emotion_score * W_EMOTION) +
        (pause_score * W_PAUSES) +
        (eye_score * W_EYE) +
        (blink_score * W_BLINK)
    )
    
    return {
        "final_score": round(final_score, 1),
        "breakdown": {
            "filler_score": round(filler_score, 1),
            "wpm_score": round(wpm_score, 1),
            "sentiment_score": round(sentiment_score, 1),
            "emotion_score": round(emotion_score, 1),
            "pause_score": round(pause_score, 1),
            "eye_score": round(eye_score, 1),
            "blink_score": round(blink_score, 1)
        }
    }
