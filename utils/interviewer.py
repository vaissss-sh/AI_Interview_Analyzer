import json
import os
import random

def load_question_bank(role: str) -> dict:
    """Loads a question bank from JSON based on the role."""
    # Convert spaces/slashes to underscores and lower case
    role_key = role.lower().replace(" ", "_").replace("-", "_")
    filepath = os.path.join("data", "question_bank", f"{role_key}.json")
    
    if not os.path.exists(filepath):
        # Fallback to software_engineer if specific role not found
        filepath = os.path.join("data", "question_bank", "software_engineer.json")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_questions_for_role(role: str, difficulty: str, count: int) -> list:
    """
    Selects balanced questions (mix of technical, behavioral, situational)
    based on the role and difficulty level.
    """
    bank = load_question_bank(role)
    diff_key = difficulty.lower()
    
    if diff_key not in bank:
        # Fallback to mid if strict string matching fails
        diff_key = "mid"
        
    available_qs = bank[diff_key]
    
    # Simple random selection for now, prioritized by category could be added
    if count > len(available_qs):
        return available_qs
        
    return random.sample(available_qs, count)

def categorize_question(q: dict) -> str:
    """Returns the theoretical category of a question."""
    return q.get("category", "general")

def generate_followup(answer: str, context: str) -> str:
    """
    Dynamically generates a follow-up question.
    In a full LLM implementation, this would call GPT-4/Claude.
    For MVP, we use keyword heuristics if not hooked to LLM directly.
    """
    # Basic heuristic baseline if LLM is unavailable
    if "failed" in answer.lower() or "mistake" in answer.lower():
        return "Can you elaborate on what specific steps you took to correct that mistake?"
    if len(answer.split()) < 20: 
        return "Could you provide a more detailed example featuring the STAR method?"
        
    return "That's interesting. What was the biggest challenge in that specific situation?"
