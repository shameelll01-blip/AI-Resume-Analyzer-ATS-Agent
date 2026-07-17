from skills import extract_skills

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Warning: Failed to load SentenceTransformer: {e}. Falling back to TF-IDF scoring.")
    model = None


def semantic_score(resume, job):
    if model is not None:
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            emb1 = model.encode([resume])
            emb2 = model.encode([job])
            return cosine_similarity(emb1, emb2)[0][0] * 100
        except Exception as e:
            print(f"SentenceTransformer encoding failed: {e}. Falling back to TF-IDF.")
            
    # Heuristic fallback using TF-IDF cosine similarity
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([resume, job])
        return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100
    except Exception as e:
        print(f"TF-IDF calculation failed: {e}. Falling back to simple Jaccard index.")
        # Simple word-overlap fallback
        words1 = set(resume.lower().split())
        words2 = set(job.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        return (len(intersection) / len(words2)) * 100


def calculate_score(resume_text, job_text):
    resume_skills = extract_skills(resume_text.lower())
    job_skills = extract_skills(job_text.lower())

    matched = set(resume_skills).intersection(set(job_skills))

    if len(job_skills) == 0:
        return 0.0, [], job_skills, 0.0

    skill_score = (len(matched) / len(job_skills)) * 100
    missing = sorted(set(job_skills) - matched)
    semantic = semantic_score(resume_text, job_text)
    final = round((0.6 * skill_score) + (0.4 * semantic), 2)

    return round(skill_score, 2), matched, missing, final


def get_suggestions(missing_skills):
    suggestions = []

    if missing_skills:
        suggestions.append(f"Add these skills: {', '.join(missing_skills)}")

    suggestions.append("Use more action verbs like built, developed, created")
    suggestions.append("Add measurable achievements (numbers, percentages)")
    suggestions.append("Improve formatting and use keywords from job description")

    return suggestions


if __name__ == '__main__':
    resume = 'Experienced Python developer with SQL and machine learning skills.'
    job = 'Looking for a Python engineer with SQL, data analysis, and machine learning experience.'
    skill_score, matched, missing, final_score = calculate_score(resume, job)
    print('Skill score:', skill_score)
    print('Matched skills:', matched)
    print('Missing skills:', missing)
    print('Final score:', final_score)


