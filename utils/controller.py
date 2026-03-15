import streamlit as st
from datetime import datetime
from utils.db import save_session

def init_session_state():
    """Initializes default Streamlit session_state variables."""
    if 'interview_active' not in st.session_state:
        st.session_state.interview_active = False
    if 'paused' not in st.session_state:
        st.session_state.paused = False
    if 'current_q_index' not in st.session_state:
        st.session_state.current_q_index = 0
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {}
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'emotions_timeline' not in st.session_state:
        st.session_state.emotions_timeline = []
    if 'current_answer_transcript' not in st.session_state:
        st.session_state.current_answer_transcript = ""

def start_interview(candidate_info: dict, role: str, questions: list):
    """Sets up state to begin an interview."""
    st.session_state.candidate_info = candidate_info
    st.session_state.candidate_info['role'] = role
    
    # Store questions as dicts with answer fields
    st.session_state.questions = []
    for q in questions:
        st.session_state.questions.append({
            "text": q.get("question", ""),
            "category": q.get("category", ""),
            "id": q.get("id"),
            "answer_transcript": "",
            "score": 0.0
        })
        
    st.session_state.current_q_index = 0
    st.session_state.interview_active = True
    st.session_state.paused = False
    st.session_state.start_time = datetime.utcnow()
    st.session_state.emotions_timeline = []
    st.session_state.current_answer_transcript = ""

def end_interview():
    """Finishes the interview, triggers scoring, handles DB save."""
    # Ensure active answer is saved to current question
    if st.session_state.questions and st.session_state.current_q_index < len(st.session_state.questions):
        st.session_state.questions[st.session_state.current_q_index]['answer_transcript'] = st.session_state.current_answer_transcript

    st.session_state.interview_active = False
    st.session_state.paused = False
    
    # Prepare session data to save
    session_data = {
        "name": st.session_state.candidate_info.get("name", "Unknown"),
        "email": st.session_state.candidate_info.get("email", "unknown@example.com"),
        "role": st.session_state.candidate_info.get("role", "Unknown"),
        "start_time": st.session_state.start_time,
        "questions": st.session_state.questions,
        "emotions": st.session_state.emotions_timeline,
    }
    
    # ── Real NLP Analysis on Transcripts ──────────────────────────────
    from scoring.rubric import load_rubric
    from scoring.fusion import fuse_scores
    from nlp.engine import analyze_answer, get_answer_sentiment_arc
    from nlp.star_detector import detect_star_components
    from nlp.keyword_matcher import match_answer_to_jd
    
    role = st.session_state.candidate_info.get("role", "software_engineer")
    rubric = load_rubric(role)
    jd_text = st.session_state.candidate_info.get("jd_text", "")
    
    # Analyze each question's transcript with real NLP
    all_transcripts = []
    total_word_count = 0
    total_vocab_score = 0
    total_completeness = 0
    total_sentiment = 0
    total_star = 0
    total_keyword_coverage = 0
    scored_count = 0
    
    for q in st.session_state.questions:
        transcript = q.get("answer_transcript", "")
        all_transcripts.append(transcript)
        
        if transcript.strip():
            # Run NLP engine analysis
            nlp_result = analyze_answer(transcript, q.get("text", ""))
            star_result = detect_star_components(transcript)
            
            # Keyword matching against JD if provided
            if jd_text:
                kw_result = match_answer_to_jd(transcript, jd_text)
                kw_coverage = kw_result.get("coverage_percent", 50)
            else:
                kw_coverage = 50  # Default when no JD
            
            # Per-question score: weighted combo of NLP metrics
            q_score = (
                nlp_result["vocabulary_score"] * 0.2 +
                nlp_result["completeness"] * 0.2 +
                nlp_result["sentiment"] * 0.15 +
                star_result["star_score"] * 0.25 +
                kw_coverage * 0.2
            )
            q["score"] = round(min(100, max(0, q_score)), 1)
            
            # Accumulate for fusion
            total_vocab_score += nlp_result["vocabulary_score"]
            total_completeness += nlp_result["completeness"]
            total_sentiment += nlp_result["sentiment"]
            total_star += star_result["star_score"]
            total_keyword_coverage += kw_coverage
            total_word_count += len(transcript.split())
            scored_count += 1
        else:
            q["score"] = 0.0
    
    # Compute averages for fusion
    n = max(1, scored_count)
    avg_vocab = total_vocab_score / n
    avg_completeness = total_completeness / n
    avg_sentiment = total_sentiment / n
    avg_star = total_star / n
    avg_kw = total_keyword_coverage / n
    
    # Estimate WPM from total words and interview duration
    duration_secs = (datetime.utcnow() - st.session_state.start_time).total_seconds()
    estimated_wpm = (total_word_count / max(1, duration_secs)) * 60
    
    # Build realistic fusion inputs from actual data
    audio_data = {
        "wpm": round(estimated_wpm),
        "fillers": {},
        "voice_confidence": round(min(100, avg_sentiment * 0.5 + avg_completeness * 0.5)),
        "silence_ratio": 0.15 if scored_count > 0 else 0.9
    }
    
    # Use real emotion data if captured
    emotions_list = st.session_state.emotions_timeline
    emotion_summary = {}
    stress_count = 0
    for e in emotions_list:
        emo = e.get("emotion", "neutral")
        emotion_summary[emo] = emotion_summary.get(emo, 0) + 1
        if emo in ["fear", "angry", "disgust"]:
            stress_count += 1
    
    eye_contact_pct = st.session_state.candidate_info.get("eye_contact_percent", 70)
    posture_val = st.session_state.candidate_info.get("posture_summary", "upright")
    
    vision_data = {
        "eye_contact_percent": eye_contact_pct,
        "posture": posture_val,
        "emotion_summary": emotion_summary,
        "stress_spikes": stress_count
    }
    
    nlp_data = {
        "vocabulary_score": round(avg_vocab, 1),
        "completeness": round(avg_completeness, 1),
        "keyword_coverage_percent": round(avg_kw, 1),
        "star_score": round(avg_star, 1),
        "sentiment": round(avg_sentiment, 1)
    }
    
    if scored_count == 0:
        session_data["overall_score"] = 0.0
        session_data["grade"] = "N/A (No Speech Detected)"
        session_data["score_breakdown"] = {
            "communication": 0.0,
            "confidence": 0.0,
            "technical": 0.0,
            "emotional_iq": 0.0,
            "engagement": 0.0,
            "professionalism": 0.0
        }
    else:
        fusion_result = fuse_scores(audio_data, vision_data, nlp_data, rubric)
        
        session_data["overall_score"] = fusion_result["overall_score"]
        session_data["grade"] = fusion_result["grade"]
        session_data["score_breakdown"] = fusion_result["breakdown"]
    
    # Actually saving happens gracefully.
    session_id = save_session(session_data)
    st.session_state.last_session_id = session_id

def get_current_question() -> str:
    """Returns the text of the current question."""
    if not st.session_state.questions:
        return ""
    idx = st.session_state.current_q_index
    if idx < len(st.session_state.questions):
        return st.session_state.questions[idx]["text"]
    return "Interview Complete."

def next_question():
    """Advances to the next question."""
    idx = st.session_state.current_q_index
    
    # Save transcript to current question before moving
    if idx < len(st.session_state.questions):
        st.session_state.questions[idx]['answer_transcript'] = st.session_state.current_answer_transcript
    
    st.session_state.current_answer_transcript = "" # Clear for next question
    
    if idx < len(st.session_state.questions) - 1:
        st.session_state.current_q_index += 1
    else:
        end_interview()

def pause_interview():
    """Pauses the interview logic/timers."""
    st.session_state.paused = True

def resume_interview():
    """Resumes a paused interview."""
    st.session_state.paused = False

def get_session_summary() -> dict:
    """Returns a brief summary of the completed interview."""
    return {
        "candidate": st.session_state.candidate_info,
        "total_questions": len(st.session_state.questions),
        "duration_seconds": (datetime.utcnow() - st.session_state.start_time).total_seconds() if st.session_state.start_time else 0
    }
