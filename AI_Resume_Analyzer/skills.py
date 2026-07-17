SKILLS_DB = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go",
    "ruby", "php", "swift", "kotlin", "react", "node.js", "django",
    "flask", "spring boot", "fastapi", "angular", "vue", "docker",
    "kubernetes", "aws", "azure", "gcp", "linux", "bash", "git",
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle",
    "machine learning", "deep learning", "nlp", "computer vision",
    "artificial intelligence", "data analysis", "data analytics",
    "data visualization", "statistics", "excel", "power bi", "tableau",
    "spark", "hadoop", "etl", "data warehousing", "snowflake",
    "bigquery", "pandas", "numpy", "scikit-learn", "tensorflow",
    "pytorch", "jupyter", "r", "matlab", "business intelligence",
    "mlops", "devops", "ci/cd", "terraform", "ansible", "jira",
    "agile", "scrum", "product management", "ui/ux", "figma",
    "testing", "selenium", "pytest", "manual testing", "quality assurance",
    "cybersecurity", "networking", "cloud computing", "communication",
    "leadership", "project management", "stakeholder management",
    "salesforce", "crm", "digital marketing", "seo", "content writing",
    "copywriting", "social media", "graphic design", "photoshop",
    "video editing", "accounting", "finance", "audit", "sap",
    "hr", "recruiting", "customer support", "operations", "logistics"
]


def extract_skills(text):
    found = []
    for skill in SKILLS_DB:
        if skill in text:
            found.append(skill)
    return found
