import re

def detect_star_components(text: str) -> dict:
    """
    Analyzes an answer to see if it follows the STAR framework 
    (Situation, Task, Action, Result).
    Returns boolean mapping and an overall STAR score.
    """
    text_lower = text.lower()
    
    # Heuristic indicator words for each section
    indicators = {
        "situation": ["when i was", "at my previous", "during my time", "context", "situation", "problem was", "issue was"],
        "task": ["my role", "my objective", "my responsibility", "i had to", "goal was", "tasked with", "my task was"],
        "action": ["i decided to", "i implemented", "i created", "i built", "i led", "i analyzed", "i resolved"],
        "result": ["as a result", "consequently", "the outcome", "achieved", "increased by", "decreased by", "led to", "finally"]
    }
    
    components = {
        "situation": False,
        "task": False,
        "action": False,
        "result": False
    }
    
    for comp, words in indicators.items():
        if any(word in text_lower for word in words):
            components[comp] = True
            
    # Special parsing for action: usually the longest chunk starting with "I"
    if text_lower.count(" i ") > 3:
        components["action"] = True
        
    score = sum(1 for v in components.values() if v) / 4.0 * 100
    
    return {
        "situation": components["situation"],
        "task": components["task"],
        "action": components["action"],
        "result": components["result"],
        "star_score": score
    }

def highlight_star_segments(text: str) -> dict:
    """
    Attempts to break the text into the 4 STAR components for highlighting in the UI.
    Returns {'situation': '...', 'task': '...', 'action': '...', 'result': '...'}
    """
    # Without an LLM, this relies on splitting the string roughly into 4 chunks based on heuristics.
    # We will do a generic proportional split for demonstration, 
    # assuming a well formed answer has 15% S, 15% T, 50% A, 20% R length-wise.
    
    words = text.split()
    total = len(words)
    
    if total < 20: # Too short to properly divide
        return {"situation": "", "task": "", "action": text, "result": ""}
        
    s_idx = int(total * 0.15)
    t_idx = s_idx + int(total * 0.15)
    a_idx = t_idx + int(total * 0.50)
    
    return {
        "situation": " ".join(words[:s_idx]),
        "task": " ".join(words[s_idx:t_idx]),
        "action": " ".join(words[t_idx:a_idx]),
        "result": " ".join(words[a_idx:])
    }

def get_star_feedback(star_dict: dict) -> str:
    """
    Generates a coaching tip based on missing STAR components.
    """
    missing = [k.capitalize() for k, v in star_dict.items() if k != "star_score" and not v]
    
    if not missing:
        return "Excellent use of the STAR method!"
        
    if "Result" in missing:
        return "You forgot to mention the outcome! Always end by sharing the Results of your actions."
        
    if "Action" in missing:
        return "Focus more on the Actions YOU took, rather than just what the team did."
        
    return f"Try to clarify the {', '.join(missing)} to give your answer better structure."
