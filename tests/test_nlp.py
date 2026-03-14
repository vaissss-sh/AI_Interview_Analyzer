import pytest
from nlp.star_detector import detect_star_components, highlight_star_segments
from nlp.keyword_matcher import extract_jd_keywords, match_answer_to_jd

def test_star_detection_perfect():
    answer = """
    When I was at TechCorp, the problem was that our app was crashing daily. 
    My task was to stabilize the backend. 
    I led a small team and I implemented a new caching layer using Redis. 
    As a result, downtime decreased by 99% and revenue increased.
    """
    res = detect_star_components(answer)
    assert res["situation"] is True
    assert res["task"] is True
    assert res["action"] is True
    assert res["result"] is True
    assert res["star_score"] == 100.0

def test_star_detection_poor():
    answer = "We just built a thing and it worked out fine. We used Python."
    res = detect_star_components(answer)
    assert res["star_score"] < 50.0

def test_highlight_segments():
    answer = "I " * 40 # 40 words
    segs = highlight_star_segments(answer)
    # S 15%, T 15%, A 50%, R 20%
    assert len(segs["situation"].split()) == 6
    assert len(segs["task"].split()) == 6
    assert len(segs["action"].split()) == 20
    assert len(segs["result"].split()) == 8

def test_jd_keyword_matcher():
    jd = "We need a strong Python developer with AWS and Docker experience. Agile is a must."
    kws = extract_jd_keywords(jd)
    
    assert "python" in kws
    assert "aws" in kws
    assert "docker" in kws
    assert "agile" in kws
    
    answer = "I have coded in Python for years and deployed to AWS frequently."
    score = match_answer_to_jd(answer, kws)
    # 2 out of 4 matches => 50%. Our formula does 0.5 * 200 = 100 max
    assert score == 100.0
