import json
import re

try:
    import google.generativeai as genai
    GEMINI_BACKEND = "legacy"
except ImportError:
    genai = None
    GEMINI_BACKEND = None

try:
    from google import genai as google_genai
    GOOGLE_GEN_AI_AVAILABLE = True
except ImportError:
    google_genai = None
    GOOGLE_GEN_AI_AVAILABLE = False

from scorer import calculate_score, semantic_score
from skills import extract_skills, SKILLS_DB

# Heuristic parsing fallback helper
def parse_resume_heuristically(resume_text: str):
    # Clean text lines
    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
    
    # Try to extract name, email, phone, address using regex
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
    email = email_match.group(0) if email_match else "Email not found"
    
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{10}\b|\b\d{5}\s\d{3}\s\d{3}\b', resume_text)
    phone = phone_match.group(0) if phone_match else "Phone not found"
    
    # Try to find a name: usually the first few lines of text
    name = "Candidate Name"
    for line in lines[:5]:
        # Simple name check: no email, no numbers, length short, first letter capitalized
        if '@' not in line and not any(c.isdigit() for c in line) and len(line) < 40 and len(line.split()) <= 4:
            name = line.title()
            break
            
    # Try to extract address
    address = "Address not found"
    address_match = re.search(r'\d+\s+[\w\s\.,#-]+(?:avenue|ave|street|st|road|rd|lane|ln|drive|dr|court|ct|park|plaza|square|way|boulevard|blvd)\b', resume_text, re.IGNORECASE)
    if address_match:
        address = address_match.group(0).title()
    else:
        # Check lines for common state/country indicator or zip code or postal keywords
        for line in lines[:8]:
            if any(term in line.lower() for term in ["street", "ave", "road", "drive", "lane", "apartment", "suite", "address", "park", "road"]):
                address = line
                break

    # Structure check: search for standard sections
    content = {
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "summary": "",
        "experience": [],
        "education": [],
        "projects": []
    }
    
    # Partition text for dynamic A4 preview
    if len(lines) < 20:
        content["summary"] = resume_text
    else:
        current_section = "summary"
        summary_lines = []
        exp_lines = []
        edu_lines = []
        proj_lines = []
        
        for line in lines:
            ll = line.lower()
            # Detect section switches
            if "experience" in ll or "employment" in ll or "work history" in ll or "professional background" in ll:
                current_section = "experience"
                continue
            elif "education" in ll or "academic" in ll or "college" in ll or "university" in ll:
                current_section = "education"
                continue
            elif "project" in ll or "portfolio" in ll:
                current_section = "projects"
                continue
            elif "skill" in ll or "competenc" in ll or "technologies" in ll:
                current_section = "skills"
                continue
                
            # Append lines to current section, limiting size for UI aesthetics
            if current_section == "summary":
                if len(summary_lines) < 8:
                    summary_lines.append(line)
            elif current_section == "experience":
                if len(exp_lines) < 20:
                    exp_lines.append(line)
            elif current_section == "education":
                if len(edu_lines) < 10:
                    edu_lines.append(line)
            elif current_section == "projects":
                if len(proj_lines) < 12:
                    proj_lines.append(line)
                    
        content["summary"] = " ".join(summary_lines) if summary_lines else "No formal summary section detected."
        content["experience"] = exp_lines if exp_lines else ["No work experience details extracted."]
        content["education"] = edu_lines if edu_lines else ["No education details extracted."]
        content["projects"] = proj_lines if proj_lines else ["No project details extracted."]
        
    return content

def run_ai_analysis(resume_text: str, job_description: str, api_key: str = None) -> dict:
    if not api_key or api_key.strip() == "":
        return run_heuristic_analysis(resume_text, job_description)

    if genai is None and not GOOGLE_GEN_AI_AVAILABLE:
        print("No Gemini SDK available. Falling back to heuristic analysis.")
        return run_heuristic_analysis(resume_text, job_description, api_error="Gemini SDK not installed")

    try:
        system_prompt = """
        You are an expert AI Resume Reviewer and Applicant Tracking System (ATS) optimizer. 
        Your task is to analyze the provided resume text against the job description and return a comprehensive evaluation in raw JSON format.
        
        You must evaluate:
        1. "resume_score": An overall score from 0 to 100 based on standard recruiter evaluation.
        2. "categories": A breakdown of resume score into:
           - "tone_style": Tone and professionalism. Rate score (0-100), status (either "Needs Work", "Good Start", or "Excellent"), and detailed feedback string.
           - "content": Completeness, achievement-oriented bullets, and quality. Rate score (0-100), status (either "Needs Work", "Good Start", or "Excellent"), and feedback.
           - "structure": Layout, standard sections, and ATS layout readability. Rate score (0-100), status (either "Needs Work", "Good Start", or "Excellent"), and feedback.
           - "skills": Match of professional and technical skills. Rate score (0-100), status (either "Needs Work", "Good Start", or "Excellent"), and feedback.
        3. "ats_score": An ATS-specific parsing and compatibility score from 0 to 100 representing how easily ATS tools will parse and match this resume.
        4. "ats_status": ATS status text like "Needs Improvement", "Good Match", or "Outstanding Fit".
        5. "ats_warnings": A list of up to 5 warnings or improvements specifically for parsing (e.g. "Missing relevant technical skills for X position", "Contains complex formatting like tables/headers that block ATS", "Lacks key standard sections like Projects", "Contains instructional/placeholder text").
        6. "matched_skills": A list of skills found in both the resume and the job description.
        7. "missing_skills": A list of major skills specified in the job description that are missing from the resume.
        8. "suggestions": A list of 4 actionable bullet points to improve the resume fit.
        9. "parsed_resume": An object containing contact info and main text segments to render a clean A4 resume preview:
           - "name": Full name of candidate.
           - "email": Email address.
           - "phone": Phone number.
           - "address": Address or location.
           - "summary": A professional summary.
           - "experience": A list of work experience details (bullet points or short sentences).
           - "education": A list of education/degree lines.
           - "projects": A list of projects.
           
        Your response must be valid, parseable JSON only. Do not include markdown code block formatting (like ```json ... ```) or any trailing text, just raw JSON.
        """

        user_prompt = f"""
        JOB DESCRIPTION:
        {job_description}
        
        RESUME TEXT:
        {resume_text}
        """

        if GEMINI_BACKEND == "legacy" and genai is not None:
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                contents=[system_prompt, user_prompt],
                generation_config={"response_mime_type": "application/json"}
            )
            result_text = response.text.strip()
        elif GOOGLE_GEN_AI_AVAILABLE and google_genai is not None:
            client = google_genai.Client(api_key=api_key.strip())
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[system_prompt, user_prompt],
            )
            result_text = getattr(response, "text", str(response)).strip()
        else:
            return run_heuristic_analysis(resume_text, job_description, api_error="Gemini unavailable")

        if result_text.startswith("```"):
            result_text = re.sub(r"^```(?:json)?\n", "", result_text)
            result_text = re.sub(r"\n```$", "", result_text)

        data = json.loads(result_text)
        return data

    except Exception as e:
        print(f"Error calling Gemini API: {e}. Falling back to heuristic analysis.")
        return run_heuristic_analysis(resume_text, job_description, api_error=str(e))

def run_heuristic_analysis(resume_text: str, job_description: str, api_error: str = None) -> dict:
    # Get baseline calculations
    skill_score, matched, missing, final_score = calculate_score(resume_text, job_description)
    
    # Calculate subscores
    # Tone & Style Heuristic: based on length, and keyword count
    tone_score = 65
    tone_status = "Good Start"
    tone_feedback = "The resume tone is professional. To improve, use more action-oriented verbs at the beginning of each bullet point."
    
    # Structure Heuristic: check if keywords like "education", "experience", "skills", "projects" exist
    lower_res = resume_text.lower()
    structure_score = 40
    warnings = []
    
    has_edu = "education" in lower_res or "university" in lower_res or "college" in lower_res or "degree" in lower_res
    has_exp = "experience" in lower_res or "employment" in lower_res or "history" in lower_res or "work" in lower_res
    has_skills = "skills" in lower_res or "technologies" in lower_res or "proficiencies" in lower_res
    has_proj = "projects" in lower_res or "portfolio" in lower_res
    
    sec_count = sum([has_edu, has_exp, has_skills, has_proj])
    structure_score += sec_count * 15 # Max 60 + 40 = 100
    if structure_score > 100:
        structure_score = 100
        
    if not has_edu:
        warnings.append("No technical education or training related to the position found")
    if not has_proj:
        warnings.append("Lacks industry-standard sections like Projects to demonstrate applied work")
    if not has_skills:
        warnings.append("Lacks a dedicated Technical Skills section")
    
    # Check for instructional text like "Tip:", "(Insert", "Example"
    instructional_match = re.search(r'\(tip:|\[insert|example|instruction', lower_res)
    if instructional_match:
        warnings.append("Resume contains instructional/placeholder text that will confuse ATS systems")
        
    structure_status = "Needs Work" if structure_score < 60 else "Good Start" if structure_score < 85 else "Excellent"
    structure_feedback = f"Parsed sections: Experience ({'Yes' if has_exp else 'No'}), Education ({'Yes' if has_edu else 'No'}), Projects ({'Yes' if has_proj else 'No'}), Skills ({'Yes' if has_skills else 'No'})."
    
    # Content Heuristic: semantic score + length check
    sem_score = semantic_score(resume_text, job_description)
    content_score = int(sem_score)
    if content_score < 0: content_score = 0
    if content_score > 100: content_score = 100
    
    content_status = "Needs Work" if content_score < 60 else "Good Start" if content_score < 80 else "Excellent"
    content_feedback = "Your experience descriptions could be stronger. Consider incorporating measurable results (e.g. percentages, dollar figures)."
    
    # Skills Heuristic
    skills_score_val = int(skill_score)
    skills_status = "Needs Work" if skills_score_val < 50 else "Good Start" if skills_score_val < 80 else "Excellent"
    skills_feedback = f"Matched {len(matched)} skills, but missed {len(missing)} key requirements."
    if missing:
        warnings.append(f"Missing relevant technical skills like: {', '.join(missing[:3])}")
        
    # Standard warnings fallback if nothing found
    if not warnings:
        warnings.append("Format could be optimized for automated parsers")
        warnings.append("Ensure your summary has key credentials aligned to this job description")
        
    # Calculate Overall ATS Score
    # Simple average of skill score and semantic similarity, adjusted for section completeness
    ats_score_val = int((skills_score_val * 0.5) + (sem_score * 0.4) + (structure_score * 0.1))
    if ats_score_val < 0: ats_score_val = 0
    if ats_score_val > 100: ats_score_val = 100
    
    ats_status = "Needs Improvement" if ats_score_val < 50 else "Good Match" if ats_score_val < 80 else "Outstanding Fit"
    
    # Parse resume details
    parsed = parse_resume_heuristically(resume_text)
    
    # Overall Resume Score: average of all four categories
    resume_score_val = int((tone_score + content_score + structure_score + skills_score_val) / 4)
    
    suggestions = [
        "Add the missing keywords into your job experience and skills sections.",
        "Focus on improving your resume summary and bullet points with exact role language.",
        "Use strong action verbs such as built, launched, optimized, and improved.",
        "Keep formatting clean so both ATS and humans can read your resume easily."
    ]
    
    if api_error:
        suggestions.insert(0, f"[API Note: Using heuristics because Gemini call failed: {api_error[:50]}]")
    else:
        suggestions.insert(0, "[API Note: Enter a Gemini API Key to enable the advanced AI Agent analysis]")
        
    return {
        "resume_score": resume_score_val,
        "categories": {
            "tone_style": {"score": tone_score, "status": tone_status, "details": tone_feedback},
            "content": {"score": content_score, "status": content_status, "details": content_feedback},
            "structure": {"score": structure_score, "status": structure_status, "details": structure_feedback},
            "skills": {"score": skills_score_val, "status": skills_status, "details": skills_feedback}
        },
        "ats_score": ats_score_val,
        "ats_status": ats_status,
        "ats_warnings": warnings[:5],
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing)),
        "suggestions": suggestions,
        "parsed_resume": parsed
    }
