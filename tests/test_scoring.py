import pytest
from scoring.rubric import load_rubric, get_grade
from scoring.fusion import fuse_scores, detect_authenticity_score

def test_rubric_load():
    swe = load_rubric("Software Engineer")
    assert swe["weight"] == "standard"
    assert "python" in swe["keywords"]
    
    pm = load_rubric("Product Manager")
    assert "roadmap" in pm["keywords"]
    
    default = load_rubric("unknown_role")
    assert default["weight"] == "standard"

def test_get_grade():
    assert get_grade(95) == "A (Excellent)"
    assert get_grade(85) == "B (Good)"
    assert get_grade(75) == "C (Passable)"
    assert get_grade(65) == "D (Needs Improvement)"
    assert get_grade(50) == "F (Fail)"

def test_fuse_scores():
    audio = {"wpm": 140, "fillers": {"um": 1}, "voice_confidence": 80, "silence_ratio": 0.1}
    vision = {"eye_contact_percent": 85, "posture": "upright", "emotion_summary": {"happy": 40}, "stress_spikes": 0}
    nlp = {"vocabulary_score": 80, "completeness": 90, "keyword_coverage_percent": 80, "star_score": 90, "sentiment": 75}
    rubric = load_rubric("software_engineer")
    
    res = fuse_scores(audio, vision, nlp, rubric)
    
    bd = res["breakdown"]
    assert 0 <= bd["communication"] <= 100
    assert 0 <= bd["confidence"] <= 100
    assert 0 <= bd["technical"] <= 100
    assert bd["professionalism"] > 80 # Low stress, low silence
    
    assert res["grade"] in ["A (Excellent)", "B (Good)", "C (Passable)"]

def test_authenticity_score():
    assert detect_authenticity_score(2.0, [], [95, 95]) == 40.0 # Rehearsed
    assert detect_authenticity_score(30.0, [], []) == 90.0 # Genuine
