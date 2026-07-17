import os
from flask import Flask, request, jsonify, render_template
from utils import extract_text
from ats_agent import run_ai_analysis

app = Flask(__name__, template_folder='templates', static_folder='static')

# Set upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resumes')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Job description templates
JOB_TEMPLATES = {
    "Software Engineer": "We're looking for a Software Engineer to design, build, and maintain scalable applications.\n\n**Responsibilities:**\n- Write clean, efficient, and well-documented code\n- Design and implement RESTful APIs and microservices\n- Collaborate with product managers and designers to build new features\n- Debug and resolve production issues\n- Participate in code reviews and maintain coding standards\n- Write unit and integration tests\n- Optimize applications for performance and scalability\n- Work in an Agile/Scrum development environment\n\n**Required Skills:**\n- Bachelor's degree in Computer Science or equivalent experience\n- 2+ years of experience with Python, Java, or JavaScript\n- Experience with frameworks like React, Node.js, or Django\n- Solid understanding of data structures and algorithms\n- Experience with Git, CI/CD pipelines, and version control\n- Familiarity with databases (SQL and NoSQL)\n\n**Preferred Skills:**\n- Experience with Docker, Kubernetes, or cloud platforms (AWS/GCP/Azure)\n- Knowledge of system design principles\n- Exposure to microservices architecture",
    "Data Scientist": "We are seeking a Data Scientist to build predictive models and extract insights from complex datasets to solve business problems.\n\n**Responsibilities:**\n- Develop machine learning models for prediction, classification, and clustering\n- Perform exploratory data analysis and feature engineering\n- Clean and preprocess structured and unstructured data\n- Design experiments and A/B tests to validate hypotheses\n- Communicate findings through visualizations and reports\n- Deploy models into production in collaboration with engineering teams\n- Stay current with the latest ML/AI research and techniques\n\n**Required Skills:**\n- Master's or PhD in Data Science, Statistics, Computer Science, or related field\n- 3+ years of experience in machine learning and statistical modeling\n- Proficiency in Python (Pandas, NumPy, Scikit-learn) or R\n- Strong SQL skills and experience with big data tools (Spark, Hadoop)\n- Experience with deep learning frameworks (TensorFlow, PyTorch)\n- Solid understanding of statistics, probability, and experimental design\n\n**Preferred Skills:**\n- Experience with NLP or computer vision\n- Familiarity with MLOps tools (MLflow, Kubeflow)\n- Cloud platform certifications (AWS, GCP, Azure)",
    "Product Manager": "We're looking for a Product Manager to drive product strategy, roadmap, and execution for our platform.\n\n**Responsibilities:**\n- Define product vision, strategy, and roadmap\n- Gather and prioritize requirements from customers and stakeholders\n- Write clear product specs and user stories\n- Work closely with engineering, design, and marketing teams\n- Analyze product metrics and user feedback to guide decisions\n- Conduct market research and competitive analysis\n- Manage the product lifecycle from ideation to launch\n\n**Required Skills:**\n- Bachelor's degree in Business, Engineering, or related field\n- 3+ years of experience in product management\n- Strong analytical and problem-solving skills\n- Experience with Agile/Scrum methodologies\n- Excellent communication and stakeholder management skills\n- Familiarity with product analytics tools (Amplitude, Mixpanel, Google Analytics)\n\n**Preferred Skills:**\n- Technical background or experience working with engineering teams\n- Experience with A/B testing and experimentation frameworks\n- MBA or equivalent experience",
    "Digital Marketing Specialist": "We're seeking a Digital Marketing Specialist to plan and execute marketing campaigns across digital channels.\n\n**Responsibilities:**\n- Develop and manage SEO/SEM campaigns\n- Create and manage content for social media platforms\n- Analyze campaign performance using analytics tools\n- Manage email marketing campaigns and automation\n- Collaborate with design and content teams on marketing assets\n- Conduct A/B testing to optimize conversion rates\n- Manage paid advertising budgets (Google Ads, Facebook Ads)\n\n**Required Skills:**\n- Bachelor's degree in Marketing, Communications, or related field\n- 2+ years of experience in digital marketing\n- Proficiency with Google Analytics, Google Ads, and social media platforms\n- Strong understanding of SEO/SEM best practices\n- Experience with email marketing tools (Mailchimp, HubSpot)\n- Excellent writing and communication skills\n\n**Preferred Skills:**\n- Experience with marketing automation platforms\n- Knowledge of HTML/CSS for landing page edits\n- Google Ads or HubSpot certification",
    "Business Analyst": "We are looking for a Business Analyst to bridge the gap between business needs and technical solutions.\n\n**Responsibilities:**\n- Gather and document business requirements from stakeholders\n- Analyze business processes and recommend improvements\n- Create process flow diagrams and functional specifications\n- Work with IT teams to implement solutions\n- Conduct data analysis to support business decisions\n- Facilitate meetings and workshops with stakeholders\n- Prepare reports and presentations for management\n\n**Required Skills:**\n- Bachelor's degree in Business Administration, Finance, or related field\n- 2+ years of experience as a Business Analyst\n- Strong analytical and problem-solving skills\n- Proficiency in Excel, SQL, and data visualization tools\n- Experience with process modeling (BPMN, Visio)\n- Excellent communication and documentation skills\n\n**Preferred Skills:**\n- Experience with ERP systems (SAP, Oracle)\n- Knowledge of Agile methodologies\n- Business Analysis certification (CBAP, PMI-PBA)",
    "Data Analyst": "We are seeking a detail-oriented Data Analyst to join our growing analytics team. The ideal candidate will transform raw data into actionable insights that drive business decisions.\n\n**Responsibilities:**\n- Collect, clean, and analyze large datasets from multiple sources\n- Build and maintain dashboards and reports using tools like Power BI or Tableau\n- Write complex SQL queries to extract and manipulate data\n- Perform statistical analysis to identify trends, patterns, and correlations\n- Collaborate with cross-functional teams to understand business requirements\n- Present findings and recommendations to stakeholders and leadership\n- Automate recurring reports using Python or Excel macros\n- Ensure data accuracy and integrity across reporting systems\n- Support A/B testing and experiment design\n\n**Required Skills:**\n- Bachelor's degree in Statistics, Mathematics, Computer Science, Economics, or related field\n- 2+ years of experience in data analysis or business intelligence\n- Proficiency in SQL, Excel, and at least one BI tool (Tableau, Power BI, Looker)\n- Experience with Python or R for data analysis\n- Strong understanding of statistics and data visualization principles\n- Excellent communication and presentation skills\n- Ability to work with large, complex datasets\n\n**Preferred Skills:**\n- Experience with cloud data platforms (AWS, GCP, Azure)\n- Knowledge of machine learning basics\n- Familiarity with data warehousing concepts (ETL, Snowflake, BigQuery)",
    "UI/UX Designer": "We're looking for a UI/UX Designer to create intuitive and visually engaging digital experiences.\n\n**Responsibilities:**\n- Design wireframes, prototypes, and high-fidelity mockups\n- Conduct user research and usability testing\n- Collaborate with product managers and engineers to implement designs\n- Create and maintain design systems and style guides\n- Iterate on designs based on user feedback and data\n- Ensure designs are accessible and responsive across devices\n- Present design concepts to stakeholders\n\n**Required Skills:**\n- Bachelor's degree in Design, HCI, or related field\n- 2+ years of experience in UI/UX design\n- Proficiency in Figma, Sketch, or Adobe XD\n- Strong portfolio showcasing design process and outcomes\n- Understanding of user-centered design principles\n- Experience conducting user research and usability testing\n\n**Preferred Skills:**\n- Basic knowledge of HTML/CSS\n- Experience with design systems and component libraries\n- Familiarity with motion design or prototyping tools (Framer, Principle)",
    "HR Manager": "We are seeking an HR Manager to oversee recruitment, employee relations, and HR operations.\n\n**Responsibilities:**\n- Manage full-cycle recruitment and onboarding processes\n- Develop and implement HR policies and procedures\n- Handle employee relations issues and conflict resolution\n- Oversee performance management and appraisal processes\n- Ensure compliance with labor laws and regulations\n- Manage compensation and benefits programs\n- Support organizational development and training initiatives\n\n**Required Skills:**\n- Bachelor's degree in Human Resources, Business Administration, or related field\n- 4+ years of experience in HR management\n- Strong knowledge of labor laws and HR best practices\n- Excellent interpersonal and conflict-resolution skills\n- Experience with HRIS systems (Workday, BambooHR)\n- Strong organizational and multitasking abilities\n\n**Preferred Skills:**\n- SHRM or HRCI certification\n- Experience in a fast-paced startup environment\n- Knowledge of payroll processing",
    "Financial Analyst": "We are looking for a Financial Analyst to support budgeting, forecasting, and financial reporting.\n\n**Responsibilities:**\n- Prepare monthly, quarterly, and annual financial reports\n- Build and maintain financial models for forecasting and planning\n- Analyze financial performance and variance against budgets\n- Support month-end and year-end close processes\n- Conduct cost-benefit analysis for business initiatives\n- Present financial insights to management\n- Assist with budgeting and financial planning cycles\n\n**Required Skills:**\n- Bachelor's degree in Finance, Accounting, or Economics\n- 2+ years of experience in financial analysis or accounting\n- Advanced Excel skills (pivot tables, VLOOKUP, financial modeling)\n- Strong understanding of financial statements and accounting principles\n- Experience with ERP systems (SAP, Oracle, NetSuite)\n- Excellent analytical and problem-solving skills\n\n**Preferred Skills:**\n- CFA or CPA certification (or in progress)\n- Experience with Power BI or Tableau for financial reporting\n- Knowledge of financial modeling and valuation techniques",
    "DevOps Engineer": "We're seeking a DevOps Engineer to build and maintain our CI/CD pipelines and cloud infrastructure.\n\n**Responsibilities:**\n- Design, implement, and manage CI/CD pipelines\n- Automate infrastructure provisioning using Infrastructure as Code (Terraform, CloudFormation)\n- Monitor system performance and troubleshoot production issues\n- Manage containerized applications using Docker and Kubernetes\n- Implement security best practices across infrastructure\n- Collaborate with development teams to improve deployment processes\n- Maintain system reliability, scalability, and uptime\n\n**Required Skills:**\n- Bachelor's degree in Computer Science or related field\n- 3+ years of experience in DevOps or Site Reliability Engineering\n- Strong experience with AWS, GCP, or Azure\n- Proficiency with Docker, Kubernetes, and container orchestration\n- Experience with scripting languages (Bash, Python)\n- Familiarity with monitoring tools (Prometheus, Grafana, Datadog)\n\n**Preferred Skills:**\n- Certifications like AWS Certified DevOps Engineer or CKA\n- Experience with configuration management tools (Ansible, Chef, Puppet)\n- Knowledge of security compliance frameworks",
    "Content Writer": "We are looking for a Content Writer to create engaging content across blogs, websites, and marketing materials.\n\n**Responsibilities:**\n- Research and write high-quality articles, blog posts, and web copy\n- Optimize content for SEO best practices\n- Collaborate with marketing and design teams on content strategy\n- Edit and proofread content for clarity, grammar, and tone\n- Manage content calendars and meet publishing deadlines\n- Repurpose content across different formats and channels\n- Analyze content performance and adjust strategy accordingly\n\n**Required Skills:**\n- Bachelor's degree in English, Journalism, Communications, or related field\n- 2+ years of experience in content writing or copywriting\n- Excellent writing, editing, and research skills\n- Understanding of SEO principles and keyword research\n- Experience with CMS platforms (WordPress, HubSpot)\n- Strong time management and organizational skills\n\n**Preferred Skills:**\n- Experience writing for B2B or SaaS companies\n- Familiarity with tools like SEMrush, Ahrefs, or Grammarly\n- Basic knowledge of social media content strategy",
    "Cybersecurity Analyst": "We're seeking a Cybersecurity Analyst to protect our systems and data from security threats.\n\n**Responsibilities:**\n- Monitor networks and systems for security breaches\n- Investigate security incidents and conduct root cause analysis\n- Implement and maintain security tools (firewalls, IDS/IPS, SIEM)\n- Conduct vulnerability assessments and penetration testing\n- Develop and enforce security policies and procedures\n- Stay current with emerging threats and security trends\n- Provide security awareness training to employees\n\n**Required Skills:**\n- Bachelor's degree in Cybersecurity, Computer Science, or related field\n- 2+ years of experience in cybersecurity or IT security\n- Knowledge of network security protocols and tools\n- Experience with SIEM tools (Splunk, QRadar)\n- Understanding of common vulnerabilities (OWASP Top 10)\n- Strong analytical and incident response skills\n\n**Preferred Skills:**\n- Certifications like CompTIA Security+, CEH, or CISSP\n- Experience with cloud security (AWS/Azure security services)\n- Knowledge of scripting for automation (Python, PowerShell)"
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/templates')
def get_templates():
    return jsonify(JOB_TEMPLATES)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    # Check inputs
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400
    
    resume_file = request.files['resume']
    if resume_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    job_desc = request.form.get('job_desc', '')
    if not job_desc.strip():
        return jsonify({"error": "Job description cannot be empty"}), 400
        
    api_key = request.form.get('api_key', '')
    
    try:
        # Save file temporarily with a unique name to avoid collisions and locking issues
        filename = os.path.basename(resume_file.filename)
        safe_name = os.path.splitext(filename)[0].replace(' ', '_') or 'resume'
        filepath = os.path.join(UPLOAD_FOLDER, f"{safe_name}_{os.urandom(4).hex()}.pdf")
        resume_file.save(filepath)
        
        try:
            # Extract text from pdf
            resume_text = extract_text(filepath)
        finally:
            # Clean up file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except PermissionError:
                    pass
            
        if not resume_text.strip():
            return jsonify({"error": "Could not extract text from the PDF. Please check if the file contains readable text."}), 400
            
        # Run AI analysis
        results = run_ai_analysis(resume_text, job_desc, api_key)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

