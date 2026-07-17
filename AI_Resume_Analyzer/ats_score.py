from scorer import calculate_score
from skills import extract_skills


def detect_role(job_description: str) -> str:
    normalized = job_description.lower()
    if "data analyst" in normalized or "analytics" in normalized:
        return "Data Analyst"
    if "product manager" in normalized:
        return "Product Manager"
    if "software engineer" in normalized or "developer" in normalized:
        return "Software Engineer"
    if "data scientist" in normalized:
        return "Data Scientist"
    if "business analyst" in normalized:
        return "Business Analyst"
    return "ATS-focused role"


def compose_ai_summary(final_score: float, skill_score: float, matched: set, missing: list, job_keywords: list) -> str:
    role = detect_role(' '.join(job_keywords))
    if final_score >= 85:
        fit_comment = "Your resume is strong for this role and will likely perform well in ATS screening."
    elif final_score >= 70:
        fit_comment = "Your resume is a good fit, but a few keyword improvements could make it even stronger."
    else:
        fit_comment = "Your resume needs more alignment with the job description to improve ATS performance."

    keyword_comment = f"You matched {len(matched)} of {len(job_keywords)} key job keywords."
    if missing:
        top_missing = ', '.join(missing[:4])
        missing_comment = f"Key missing terms include: {top_missing}."
    else:
        missing_comment = "You have matched all major job keywords."

    return f"{fit_comment} {keyword_comment} {missing_comment}"


def compose_recommendations(missing: list, final_score: float) -> list:
    recommendations = []
    if missing:
        recommendations.append("Add the missing keywords above into your job experience and skills sections.")
    else:
        recommendations.append("Great job matching the core keywords — keep the content concise and relevant.")

    if final_score < 70:
        recommendations.append("Focus on improving your resume summary and bullet points with the exact role language.")
    else:
        recommendations.append("Continue highlighting measurable accomplishments and tools used.")

    recommendations.append("Use strong action verbs such as built, launched, optimized, and improved.")
    recommendations.append("Keep formatting clean so both ATS and humans can read your resume easily.")
    return recommendations


def analyze_resume_for_ats(resume_text: str, job_description: str) -> dict:
    skill_score, matched, missing, final_score = calculate_score(resume_text, job_description)
    job_keywords = extract_skills(job_description.lower())
    summary = compose_ai_summary(final_score, skill_score, matched, missing, job_keywords)
    recommendations = compose_recommendations(missing, final_score)

    return {
        "skill_score": skill_score,
        "matched": matched,
        "missing": missing,
        "final_score": final_score,
        "job_keywords": job_keywords,
        "summary": summary,
        "recommendations": recommendations,
    }
