RUBRICS = {
    "software_engineer": {
        "weight": "standard",
        "keywords": ["python", "java", "architecture", "microservices", "agile", "sql", "testing"],
        "benchmark_scores": {"communication": 75, "technical": 85, "confidence": 70},
        "question_categories": ["technical", "behavioral", "situational", "problem-solving"]
    },
    "product_manager": {
        "weight": "standard",
        "keywords": ["vision", "roadmap", "strategy", "metrics", "data", "stakeholders", "users", "launch"],
        "benchmark_scores": {"communication": 85, "technical": 65, "confidence": 80, "leadership": 80},
        "question_categories": ["strategy", "behavioral", "situational", "product-sense"]
    },
    "data_scientist": {
        "weight": "standard",
        "keywords": ["model", "statistics", "machine learning", "python", "r", "validation", "pipeline"],
        "benchmark_scores": {"communication": 75, "technical": 90, "confidence": 70},
        "question_categories": ["technical", "behavioral", "situational", "strategy"]
    },
    "hr_manager": {
        "weight": "standard",
        "keywords": ["talent", "compliance", "culture", "benefits", "retention", "mediation", "diversity"],
        "benchmark_scores": {"communication": 90, "technical": 60, "confidence": 80, "emotional_iq": 90},
        "question_categories": ["strategy", "behavioral", "situational", "technical"]
    },
    "default": {
        "weight": "standard",
        "keywords": ["leadership", "teamwork", "communication", "delivery"],
        "benchmark_scores": {"communication": 75, "technical": 70, "confidence": 75},
        "question_categories": ["behavioral", "situational", "general"]
    }
}

def load_rubric(role: str) -> dict:
    """Returns the specific rubric for a given role, or default."""
    role_key = role.lower().replace(" ", "_").replace("-", "_")
    return RUBRICS.get(role_key, RUBRICS["default"])

def get_grade(total_score: float) -> str:
    """Returns an alphabetical grade based on the raw 100-point score."""
    if total_score >= 90:
        return "A (Excellent)"
    elif total_score >= 80:
        return "B (Good)"
    elif total_score >= 70:
        return "C (Passable)"
    elif total_score >= 60:
        return "D (Needs Improvement)"
    else:
        return "F (Fail)"
