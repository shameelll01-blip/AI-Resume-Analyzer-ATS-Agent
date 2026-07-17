import time
import pandas as pd
import streamlit as st
from utils import extract_text
from ats_score import analyze_resume_for_ats
from scorer import calculate_score
from skills import extract_skills

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide",
)

page_css = """
<style>
body {
    min-height: 100vh;
    background: radial-gradient(circle at top left, rgba(79, 70, 229, 0.28), transparent 25%),
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.22), transparent 22%),
                linear-gradient(135deg, #020617 0%, #081538 100%);
    color: #eef2ff;
    overflow-x: hidden;
}
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(circle at 15% 20%, rgba(96, 165, 250, 0.16) 0, transparent 24%),
        radial-gradient(circle at 80% 10%, rgba(236, 72, 153, 0.12) 0, transparent 18%),
        radial-gradient(circle at 25% 85%, rgba(168, 85, 247, 0.14) 0, transparent 22%);
    pointer-events: none;
    z-index: -1;
}
section.main {
    background: transparent;
}
.block-container {
    max-width: 1180px;
    margin: 0 auto;
    padding-top: 30px;
    padding-bottom: 30px;
}
.stApp {
    color: #eef2ff;
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.stSidebar {
    background: rgba(10, 18, 45, 0.92) !important;
    border-radius: 30px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}
.card {
    border-radius: 30px;
    padding: 32px;
    background: rgba(10, 18, 45, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
    backdrop-filter: blur(18px);
    transition: transform 0.35s ease, border-color 0.35s ease, box-shadow 0.35s ease;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top left, rgba(96, 165, 250, 0.16), transparent 22%),
                radial-gradient(circle at bottom right, rgba(168, 85, 247, 0.12), transparent 24%);
    pointer-events: none;
}
.card > * {
    position: relative;
    z-index: 1;
}
.card:hover {
    transform: translateY(-4px);
    border-color: rgba(96, 165, 250, 0.35);
    box-shadow: 0 30px 80px rgba(56, 189, 248, 0.18);
}
.animated-card {
    animation: float-card 10s ease-in-out infinite;
}
@keyframes float-card {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}
.gradient-title {
    background: linear-gradient(90deg, #86efac, #60a5fa, #c084fc);
    -webkit-background-clip: text;
    color: transparent;
}
.stButton>button {
    background: linear-gradient(135deg, #4f46e5, #0ea5e9) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 1.4rem !important;
    font-weight: 700 !important;
    box-shadow: 0 18px 40px rgba(30, 64, 175, 0.22) !important;
    transition: transform 0.25s ease !important;
}
.stButton>button:hover {
    transform: translateY(-2px) !important;
}
.chip {
    display: inline-flex;
    align-items: center;
    margin: 6px 8px 6px 0;
    padding: 10px 16px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    color: #eef2ff;
    font-size: 0.95rem;
    transition: transform 0.25s ease, background 0.25s ease;
}
.chip:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.12);
}
.chip.matched {
    background: rgba(16, 185, 129, 0.18);
    border: 1px solid rgba(34, 197, 94, 0.22);
}
.chip.missing {
    background: rgba(248, 113, 113, 0.16);
    border: 1px solid rgba(248, 113, 113, 0.28);
}
.highlight {
    color: #7dd3fc;
    font-weight: 700;
}
.pulse {
    animation: pulse 1.8s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.3); }
    70% { box-shadow: 0 0 0 18px rgba(56, 189, 248, 0); }
    100% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); }
}
.fade-in {
    animation: fadeUp 1.1s ease both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
"""

job_templates = {
    "Select a sample job role": "",
}
job_templates = {
    "Select a sample job role": "",
    "Software Engineer": "We're looking for a Software Engineer to design, build, and maintain scalable applications.\n\n**Responsibilities:**\n\n- Write clean, efficient, and well-documented code\n- Design and implement RESTful APIs and microservices\n- Collaborate with product managers and designers to build new features\n- Debug and resolve production issues\n- Participate in code reviews and maintain coding standards\n- Write unit and integration tests\n- Optimize applications for performance and scalability\n- Work in an Agile/Scrum development environment\n\n**Required Skills:**\n\n- Bachelor's degree in Computer Science or equivalent experience\n- 2+ years of experience with Python, Java, or JavaScript\n- Experience with frameworks like React, Node.js, or Django\n- Solid understanding of data structures and algorithms\n- Experience with Git, CI/CD pipelines, and version control\n- Familiarity with databases (SQL and NoSQL)\n\n**Preferred Skills:**\n\n- Experience with Docker, Kubernetes, or cloud platforms (AWS/GCP/Azure)\n- Knowledge of system design principles\n- Exposure to microservices architecture",
    "Data Scientist": "We are seeking a Data Scientist to build predictive models and extract insights from complex datasets to solve business problems.\n\n**Responsibilities:**\n\n- Develop machine learning models for prediction, classification, and clustering\n- Perform exploratory data analysis and feature engineering\n- Clean and preprocess structured and unstructured data\n- Design experiments and A/B tests to validate hypotheses\n- Communicate findings through visualizations and reports\n- Deploy models into production in collaboration with engineering teams\n- Stay current with the latest ML/AI research and techniques\n\n**Required Skills:**\n\n- Master's or PhD in Data Science, Statistics, Computer Science, or related field\n- 3+ years of experience in machine learning and statistical modeling\n- Proficiency in Python (Pandas, NumPy, Scikit-learn) or R\n- Strong SQL skills and experience with big data tools (Spark, Hadoop)\n- Experience with deep learning frameworks (TensorFlow, PyTorch)\n- Solid understanding of statistics, probability, and experimental design\n\n**Preferred Skills:**\n\n- Experience with NLP or computer vision\n- Familiarity with MLOps tools (MLflow, Kubeflow)\n- Cloud platform certifications (AWS, GCP, Azure)",
    "Product Manager": "We're looking for a Product Manager to drive product strategy, roadmap, and execution for our platform.\n\n**Responsibilities:**\n\n- Define product vision, strategy, and roadmap\n- Gather and prioritize requirements from customers and stakeholders\n- Write clear product specs and user stories\n- Work closely with engineering, design, and marketing teams\n- Analyze product metrics and user feedback to guide decisions\n- Conduct market research and competitive analysis\n- Manage the product lifecycle from ideation to launch\n\n**Required Skills:**\n\n- Bachelor's degree in Business, Engineering, or related field\n- 3+ years of experience in product management\n- Strong analytical and problem-solving skills\n- Experience with Agile/Scrum methodologies\n- Excellent communication and stakeholder management skills\n- Familiarity with product analytics tools (Amplitude, Mixpanel, Google Analytics)\n\n**Preferred Skills:**\n\n- Technical background or experience working with engineering teams\n- Experience with A/B testing and experimentation frameworks\n- MBA or equivalent experience",
    "Digital Marketing Specialist": "We're seeking a Digital Marketing Specialist to plan and execute marketing campaigns across digital channels.\n\n**Responsibilities:**\n\n- Develop and manage SEO/SEM campaigns\n- Create and manage content for social media platforms\n- Analyze campaign performance using analytics tools\n- Manage email marketing campaigns and automation\n- Collaborate with design and content teams on marketing assets\n- Conduct A/B testing to optimize conversion rates\n- Manage paid advertising budgets (Google Ads, Facebook Ads)\n\n**Required Skills:**\n\n- Bachelor's degree in Marketing, Communications, or related field\n- 2+ years of experience in digital marketing\n- Proficiency with Google Analytics, Google Ads, and social media platforms\n- Strong understanding of SEO/SEM best practices\n- Experience with email marketing tools (Mailchimp, HubSpot)\n- Excellent writing and communication skills\n\n**Preferred Skills:**\n\n- Experience with marketing automation platforms\n- Knowledge of HTML/CSS for landing page edits\n- Google Ads or HubSpot certification",
    "Business Analyst": "We are looking for a Business Analyst to bridge the gap between business needs and technical solutions.\n\n**Responsibilities:**\n\n- Gather and document business requirements from stakeholders\n- Analyze business processes and recommend improvements\n- Create process flow diagrams and functional specifications\n- Work with IT teams to implement solutions\n- Conduct data analysis to support business decisions\n- Facilitate meetings and workshops with stakeholders\n- Prepare reports and presentations for management\n\n**Required Skills:**\n\n- Bachelor's degree in Business Administration, Finance, or related field\n- 2+ years of experience as a Business Analyst\n- Strong analytical and problem-solving skills\n- Proficiency in Excel, SQL, and data visualization tools\n- Experience with process modeling (BPMN, Visio)\n- Excellent communication and documentation skills\n\n**Preferred Skills:**\n\n- Experience with ERP systems (SAP, Oracle)\n- Knowledge of Agile methodologies\n- Business Analysis certification (CBAP, PMI-PBA)",
    "Data Analyst": "We are seeking a detail-oriented Data Analyst to join our growing analytics team. The ideal candidate will transform raw data into actionable insights that drive business decisions.\n\n**Responsibilities:**\n\n- Collect, clean, and analyze large datasets from multiple sources\n- Build and maintain dashboards and reports using tools like Power BI or Tableau\n- Write complex SQL queries to extract and manipulate data\n- Perform statistical analysis to identify trends, patterns, and correlations\n- Collaborate with cross-functional teams to understand business requirements\n- Present findings and recommendations to stakeholders and leadership\n- Automate recurring reports using Python or Excel macros\n- Ensure data accuracy and integrity across reporting systems\n- Support A/B testing and experiment design\n\n**Required Skills:**\n\n- Bachelor's degree in Statistics, Mathematics, Computer Science, Economics, or related field\n- 2+ years of experience in data analysis or business intelligence\n- Proficiency in SQL, Excel, and at least one BI tool (Tableau, Power BI, Looker)\n- Experience with Python or R for data analysis\n- Strong understanding of statistics and data visualization principles\n- Excellent communication and presentation skills\n- Ability to work with large, complex datasets\n\n**Preferred Skills:**\n\n- Experience with cloud data platforms (AWS, GCP, Azure)\n- Knowledge of machine learning basics\n- Familiarity with data warehousing concepts (ETL, Snowflake, BigQuery)",
    "UI/UX Designer": "We're looking for a UI/UX Designer to create intuitive and visually engaging digital experiences.\n\n**Responsibilities:**\n\n- Design wireframes, prototypes, and high-fidelity mockups\n- Conduct user research and usability testing\n- Collaborate with product managers and engineers to implement designs\n- Create and maintain design systems and style guides\n- Iterate on designs based on user feedback and data\n- Ensure designs are accessible and responsive across devices\n- Present design concepts to stakeholders\n\n**Required Skills:**\n\n- Bachelor's degree in Design, HCI, or related field\n- 2+ years of experience in UI/UX design\n- Proficiency in Figma, Sketch, or Adobe XD\n- Strong portfolio showcasing design process and outcomes\n- Understanding of user-centered design principles\n- Experience conducting user research and usability testing\n\n**Preferred Skills:**\n\n- Basic knowledge of HTML/CSS\n- Experience with design systems and component libraries\n- Familiarity with motion design or prototyping tools (Framer, Principle)",
    "HR Manager": "We are seeking an HR Manager to oversee recruitment, employee relations, and HR operations.\n\n**Responsibilities:**\n\n- Manage full-cycle recruitment and onboarding processes\n- Develop and implement HR policies and procedures\n- Handle employee relations issues and conflict resolution\n- Oversee performance management and appraisal processes\n- Ensure compliance with labor laws and regulations\n- Manage compensation and benefits programs\n- Support organizational development and training initiatives\n\n**Required Skills:**\n\n- Bachelor's degree in Human Resources, Business Administration, or related field\n- 4+ years of experience in HR management\n- Strong knowledge of labor laws and HR best practices\n- Excellent interpersonal and conflict-resolution skills\n- Experience with HRIS systems (Workday, BambooHR)\n- Strong organizational and multitasking abilities\n\n**Preferred Skills:**\n\n- SHRM or HRCI certification\n- Experience in a fast-paced startup environment\n- Knowledge of payroll processing",
    "Financial Analyst": "We are looking for a Financial Analyst to support budgeting, forecasting, and financial reporting.\n\n**Responsibilities:**\n\n- Prepare monthly, quarterly, and annual financial reports\n- Build and maintain financial models for forecasting and planning\n- Analyze financial performance and variance against budgets\n- Support month-end and year-end close processes\n- Conduct cost-benefit analysis for business initiatives\n- Present financial insights to management\n- Assist with budgeting and financial planning cycles\n\n**Required Skills:**\n\n- Bachelor's degree in Finance, Accounting, or Economics\n- 2+ years of experience in financial analysis or accounting\n- Advanced Excel skills (pivot tables, VLOOKUP, financial modeling)\n- Strong understanding of financial statements and accounting principles\n- Experience with ERP systems (SAP, Oracle, NetSuite)\n- Excellent analytical and problem-solving skills\n\n**Preferred Skills:**\n\n- CFA or CPA certification (or in progress)\n- Experience with Power BI or Tableau for financial reporting\n- Knowledge of financial modeling and valuation techniques",
    "DevOps Engineer": "We're seeking a DevOps Engineer to build and maintain our CI/CD pipelines and cloud infrastructure.\n\n**Responsibilities:**\n\n- Design, implement, and manage CI/CD pipelines\n- Automate infrastructure provisioning using Infrastructure as Code (Terraform, CloudFormation)\n- Monitor system performance and troubleshoot production issues\n- Manage containerized applications using Docker and Kubernetes\n- Implement security best practices across infrastructure\n- Collaborate with development teams to improve deployment processes\n- Maintain system reliability, scalability, and uptime\n\n**Required Skills:**\n\n- Bachelor's degree in Computer Science or related field\n- 3+ years of experience in DevOps or Site Reliability Engineering\n- Strong experience with AWS, GCP, or Azure\n- Proficiency with Docker, Kubernetes, and container orchestration\n- Experience with scripting languages (Bash, Python)\n- Familiarity with monitoring tools (Prometheus, Grafana, Datadog)\n\n**Preferred Skills:**\n\n- Certifications like AWS Certified DevOps Engineer or CKA\n- Experience with configuration management tools (Ansible, Chef, Puppet)\n- Knowledge of security compliance frameworks",
    "Content Writer": "We are looking for a Content Writer to create engaging content across blogs, websites, and marketing materials.\n\n**Responsibilities:**\n\n- Research and write high-quality articles, blog posts, and web copy\n- Optimize content for SEO best practices\n- Collaborate with marketing and design teams on content strategy\n- Edit and proofread content for clarity, grammar, and tone\n- Manage content calendars and meet publishing deadlines\n- Repurpose content across different formats and channels\n- Analyze content performance and adjust strategy accordingly\n\n**Required Skills:**\n\n- Bachelor's degree in English, Journalism, Communications, or related field\n- 2+ years of experience in content writing or copywriting\n- Excellent writing, editing, and research skills\n- Understanding of SEO principles and keyword research\n- Experience with CMS platforms (WordPress, HubSpot)\n- Strong time management and organizational skills\n\n**Preferred Skills:**\n\n- Experience writing for B2B or SaaS companies\n- Familiarity with tools like SEMrush, Ahrefs, or Grammarly\n- Basic knowledge of social media content strategy",
    "Cybersecurity Analyst": "We're seeking a Cybersecurity Analyst to protect our systems and data from security threats.\n\n**Responsibilities:**\n\n- Monitor networks and systems for security breaches\n- Investigate security incidents and conduct root cause analysis\n- Implement and maintain security tools (firewalls, IDS/IPS, SIEM)\n- Conduct vulnerability assessments and penetration testing\n- Develop and enforce security policies and procedures\n- Stay current with emerging threats and security trends\n- Provide security awareness training to employees\n\n**Required Skills:**\n\n- Bachelor's degree in Cybersecurity, Computer Science, or related field\n- 2+ years of experience in cybersecurity or IT security\n- Knowledge of network security protocols and tools\n- Experience with SIEM tools (Splunk, QRadar)\n- Understanding of common vulnerabilities (OWASP Top 10)\n- Strong analytical and incident response skills\n\n**Preferred Skills:**\n\n- Certifications like CompTIA Security+, CEH, or CISSP\n- Experience with cloud security (AWS/Azure security services)\n- Knowledge of scripting for automation (Python, PowerShell)"
}

if "job_desc" not in st.session_state:
    st.session_state.job_desc = ""

st.markdown(page_css, unsafe_allow_html=True)

st.markdown(
    """
    <div class="card hero-section animated-card fade-in" style="margin: 0 auto 24px; max-width: 1080px;">
        <h1 class="gradient-title" style="margin-bottom: 0.3rem;">AI Resume Analyzer</h1>
        <p style="color:#c7d2fe; font-size:1.05rem;">Upload your resume PDF and paste the job description to receive a sleek ATS fit score, keyword match overview, and actionable improvement tips.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("✨ Why this analyzer")
    st.write("- Blends keyword matching with semantic alignment")
    st.write("- Presents results in a polished dashboard")
    st.write("- Highlights missing keywords and strengths")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='card' style='margin-top: 18px;'>", unsafe_allow_html=True)
    st.subheader("📌 Job description templates")
    role_choice = st.selectbox("Choose a sample role", list(job_templates.keys()))
    if role_choice != "Select a sample job role":
        if st.button("Load sample description"):
            st.session_state.job_desc = job_templates[role_choice]
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='card' style='margin-top: 18px;'>", unsafe_allow_html=True)
    st.subheader("💡 Resume tips")
    st.write("1. Mirror the job description language.")
    st.write("2. Use numbers for impact.")
    st.write("3. Keep bullet points short and scannable.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])
with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
with col2:
    job_desc = st.text_area(
        "Paste Job Description",
        height=240,
        placeholder="Paste the job description here or load a sample from the sidebar...",
        key="job_desc",
    )
st.markdown("</div>", unsafe_allow_html=True)

analyze = st.button("Analyze Resume")

if uploaded_file and job_desc and analyze:
    resume_text = extract_text(uploaded_file)
    with st.spinner("Analyzing resume and job description..."):
        progress = st.progress(0)
        for percent in range(0, 101, 20):
            time.sleep(0.1)
            progress.progress(percent)

        ats_result = analyze_resume_for_ats(resume_text, job_desc)
        skill_score = ats_result["skill_score"]
        matched = ats_result["matched"]
        missing = ats_result["missing"]
        final_score = ats_result["final_score"]
        job_keywords = ats_result["job_keywords"]
        summary = ats_result["summary"]
        recommendations = ats_result["recommendations"]
        matched_list = sorted(matched)
        missing_list = sorted(missing)

    st.markdown("<div class='card pulse'>", unsafe_allow_html=True)
    st.subheader("📊 ATS Performance")
    perf_cols = st.columns(4)
    perf_cols[0].metric("Resume Fit", f"{final_score:.2f}%")
    perf_cols[1].metric("Keyword Match", f"{skill_score:.2f}%")
    perf_cols[2].metric("Missing Skills", len(missing_list))
    perf_cols[3].metric("Job Keywords", len(job_keywords))

    st.markdown("<div style='margin-top:16px;'>", unsafe_allow_html=True)
    st.write(f"**AI Insight:** {summary}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card' style='margin-top: 18px;'>", unsafe_allow_html=True)
    st.subheader("🔧 AI Recommendations")
    for rec in recommendations:
        st.write(f"- {rec}")
    st.markdown("</div>", unsafe_allow_html=True)

    main_col, side_col = st.columns([2, 1], gap="large")
    with main_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("✅ Matched Skills")
        if matched_list:
            for skill in matched_list:
                st.markdown(f"<span class='chip matched'>{skill}</span>", unsafe_allow_html=True)
        else:
            st.info("No matched skills found.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card' style='margin-top: 18px;'>", unsafe_allow_html=True)
        st.subheader("❌ Missing Skills")
        if missing_list:
            for skill in missing_list:
                st.markdown(f"<span class='chip missing'>{skill}</span>", unsafe_allow_html=True)
        else:
            st.success("Great job — your resume already matches the job keywords.")
        st.markdown("</div>", unsafe_allow_html=True)

    with side_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("💡 Action Plan")
        if missing_list:
            st.write("Improve the resume by adding or emphasizing these:")
            for skill in missing_list:
                st.write(f"- Use **{skill}** in your experience bullets.")
        else:
            st.write("Your resume is already well-aligned with this job description.")
        st.write("- Choose strong action verbs like ‘built’, ‘optimized’, and ‘led’. ")
        st.write("- Add measurable outcomes when possible.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card' style='margin-top: 18px;'>", unsafe_allow_html=True)
        st.subheader("📌 Quick Note")
        st.write(f"Your current fit score is <span class='highlight'>{final_score}%</span>.", unsafe_allow_html=True)
        st.write("Keep refining the resume around matched keywords for stronger ATS results.")
        st.markdown("</div>", unsafe_allow_html=True)

elif analyze:
    if not uploaded_file:
        st.warning("Upload a resume PDF to continue.")
    if not job_desc:
        st.warning("Paste a job description to continue.")
else:
    st.markdown(
        """
        <div class='card' style='padding: 30px;'>
            <h3>Ready to build a standout resume?</h3>
            <p>Upload your resume and paste the job description, then press <strong>Analyze Resume</strong> to reveal an AI-powered match score and tailored suggestions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
