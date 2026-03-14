import re

def load_job_description(text_or_file: str) -> str:
    """
    Loads a job description. 
    If text_or_file is a path, reads the file (supports txt/pdf in a real implementation).
    Otherwise returns the string itself.
    """
    if len(text_or_file) < 200 and text_or_file.endswith(".txt"):
        try:
            with open(text_or_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return text_or_file

def extract_jd_keywords(jd_text: str) -> list:
    """
    Extracts important technical and soft skill keywords from the JD.
    In a full LLM version, we would prompt the LLM to extract these.
    Here we use a regex + common keywords heuristic.
    """
    # A simplified static list for demonstration
    common_jd_keywords = [
        "python", "java", "c++", "agile", "scrum", "leadership",
        "machine learning", "data science", "aws", "cloud", "docker",
        "kubernetes", "react", "node", "sql", "communication", "teamwork",
        "problem solving", "architecture", "microservices", "ci/cd",
        "testing", "design", "manage", "budget", "strategy"
    ]
    
    jd_lower = jd_text.lower()
    found_keywords = []
    
    for kw in common_jd_keywords:
        if kw in jd_lower:
            found_keywords.append(kw)
            
    # Also find any capitalized acronyms like "API", "REST", etc
    acronyms = set(re.findall(r'\b[A-Z]{3,5}\b', jd_text))
    for ac in acronyms:
        found_keywords.append(ac.lower())
        
    return list(set(found_keywords))

def match_answer_to_jd(answer: str, jd_keywords: list) -> float:
    """
    Calculates what percentage of the JD keywords are covered in the candidate's answer.
    """
    if not jd_keywords or not answer:
        return 0.0
        
    answer_lower = answer.lower()
    covered = 0
    
    for kw in jd_keywords:
        if kw in answer_lower:
            covered += 1
            
    # If they hit 50% of extracted JD keywords in a single answer, that's effectively 100% for that response
    raw_ratio = covered / len(jd_keywords)
    score = min(100.0, raw_ratio * 200) 
    
    return round(score, 2)

def get_coverage_report(all_answers: list, jd_keywords: list) -> dict:
    """
    Checks all provided answers against keywords.
    Returns: {"python": True, "aws": False, ...}
    """
    combined_answers = " ".join(all_answers).lower()
    report = {}
    
    for kw in jd_keywords:
        report[kw] = kw in combined_answers
        
    return report
