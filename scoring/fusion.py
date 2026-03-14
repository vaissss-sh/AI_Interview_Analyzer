from utils.config import SCORING_WEIGHTS

def fuse_scores(audio_scores: dict, vision_scores: dict, nlp_scores: dict, rubric: dict) -> dict:
    """
    Fuses individual module scores into the final 6 dimensions.
    Returns the fused breakdown + overall_score + grade.
    """
    
    # 1. Communication (NLP vocab + Audio pacing balance)
    vocab = nlp_scores.get("vocabulary_score", 60)
    wpm = audio_scores.get("wpm", 140)
    # Ideal pacing ~120-160 wpm; gentle penalty outside that range
    if 100 <= wpm <= 180:
        wpm_score = 85
    elif wpm == 0:
        wpm_score = 50  # No speech detected
    else:
        wpm_score = max(40, 100 - abs(140 - wpm) * 0.3)
    filler_penalty = min(15, sum(audio_scores.get("fillers", {}).values()) * 1.5)
    communication = min(100.0, max(0.0, (vocab * 0.6 + wpm_score * 0.4) - filler_penalty))

    # 2. Confidence (Voice confidence + eye contact + posture)
    voice_conf = audio_scores.get("voice_confidence", 65)
    eye_contact = vision_scores.get("eye_contact_percent", 70)
    posture_bonus = 15 if vision_scores.get("posture") == "upright" else 5
    confidence = min(100.0, max(0.0, voice_conf * 0.35 + eye_contact * 0.45 + posture_bonus + 5))

    # 3. Technical (NLP keyword match + STAR method quality)
    kw_coverage = nlp_scores.get("keyword_coverage_percent", 50)
    star_score = nlp_scores.get("star_score", 40)
    completeness = nlp_scores.get("completeness", 50)
    technical = min(100.0, max(0.0, kw_coverage * 0.4 + star_score * 0.35 + completeness * 0.25))

    # 4. Emotional IQ (Sentiment + positive emotion presence)
    sentiment = nlp_scores.get("sentiment", 55)
    emotion_summary = vision_scores.get("emotion_summary", {})
    total_emotions = max(1, sum(emotion_summary.values()))
    happy_ratio = emotion_summary.get("happy", 0) / total_emotions * 100 if emotion_summary else 40
    emotional_iq = min(100.0, max(0.0, sentiment * 0.6 + happy_ratio * 0.2 + 20))

    # 5. Engagement (Eye contact + completeness of answers)
    engagement = min(100.0, max(0.0, eye_contact * 0.5 + completeness * 0.3 + 20))

    # 6. Professionalism (Low silence + low stress + answer completeness)
    silence_ratio = audio_scores.get("silence_ratio", 0.2)
    stress_spikes = vision_scores.get("stress_spikes", 0)
    
    prof_base = 80  # Start with a reasonable baseline
    prof_base -= silence_ratio * 30  # Penalize excessive silence
    prof_base -= min(25, stress_spikes * 5)  # Penalize stress spikes
    prof_base += completeness * 0.2  # Reward complete answers
    professionalism = min(100.0, max(0.0, prof_base))

    # Compile Breakdown
    breakdown = {
        "communication": round(communication, 1),
        "confidence": round(confidence, 1),
        "technical": round(technical, 1),
        "emotional_iq": round(emotional_iq, 1),
        "engagement": round(engagement, 1),
        "professionalism": round(professionalism, 1)
    }

    # Calculate Overall using config weights
    overall_score = sum(breakdown[k] * SCORING_WEIGHTS[k] for k in breakdown.keys())
    
    from scoring.rubric import get_grade
    return {
        "breakdown": breakdown,
        "overall_score": round(overall_score, 1),
        "grade": get_grade(overall_score)
    }

def detect_authenticity_score(wpm_variance: float, answer_lengths: list, star_scores: list) -> float:
    """
    Experimental metric: Detects if answers feel rehearsed.
    Lower wpm variance = more rehearsed. 
    Returns 0-100 (100 = genuine).
    """
    if wpm_variance < 5.0 and all(s > 90 for s in star_scores):
        return 40.0  # Highly rehearsed
    elif wpm_variance > 25.0:
        return 90.0  # Very natural variations
    return 75.0  # Average

def detect_stress_index(stress_spike_count: int, max_pitch: float) -> float:
    """Returns a composite stress index (0-100) based on vision and audio data."""
    base_stress = min(100, stress_spike_count * 15)
    if max_pitch > 350:
        base_stress += 20
    return min(100.0, base_stress)
