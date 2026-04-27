"""
ai_utils.py
AI Job Preparation Assistant for GradPath AI.

Uses OpenAI's API to analyze job descriptions when an API key is configured.
Falls back to a broad rule-based analyzer if the API key is unavailable.

AI Bonus Feature:
- OpenAI-powered job description analysis when OPENAI_API_KEY exists.
- Rule-based fallback when OPENAI_API_KEY is missing or API call fails.
"""

import os
import re
import streamlit as st
from openai import OpenAI


# ── General skill keywords for fallback extraction ────────────────────────────

SKILL_CATEGORIES = {
    "Technical Skills": [
        "python", "java", "javascript", "typescript", "c++", "c#", "r", "sql",
        "html", "css", "react", "angular", "vue", "node", "node.js",
        "django", "flask", "fastapi", "spring", "api", "rest", "restful",
        "graphql", "git", "github", "gitlab", "linux", "bash", "shell",
        "docker", "kubernetes", "aws", "azure", "gcp", "cloud", "devops",
        "ci/cd", "postgresql", "mysql", "mongodb", "sqlite", "firebase",
        "supabase", "software development", "web development",
        "mobile development", "frontend", "front-end", "backend", "back-end",
        "full stack", "testing", "unit testing", "debugging", "automation",
        "cybersecurity", "information security", "networking", "system design",
    ],

    "Data and Analytics": [
        "data analysis", "data analytics", "data science", "machine learning",
        "deep learning", "artificial intelligence", "ai", "nlp", "statistics",
        "statistical analysis", "excel", "google sheets", "power bi", "powerbi",
        "tableau", "looker", "dashboard", "reporting", "data visualization",
        "forecasting", "predictive modeling", "etl", "data cleaning",
        "data mining", "business intelligence", "bi", "kpi", "metrics",
        "database", "spreadsheet", "analytics", "analysis", "insights",
        "a/b testing", "experimentation", "regression", "classification",
        "clustering",
    ],

    "Business and Operations": [
        "project management", "operations", "process improvement", "strategy",
        "business development", "stakeholder management", "customer service",
        "client relationship", "vendor management", "supply chain",
        "logistics", "quality assurance", "quality control", "risk management",
        "compliance", "documentation", "workflow", "planning", "coordination",
        "administration", "report preparation", "business analysis",
        "requirements gathering", "operational support", "process mapping",
        "scheduling", "procurement", "inventory", "sales operations",
    ],

    "Marketing and Sales": [
        "marketing", "digital marketing", "social media", "seo", "sem",
        "content creation", "copywriting", "branding", "brand", "campaigns",
        "email marketing", "market research", "sales", "lead generation",
        "customer acquisition", "crm", "hubspot", "salesforce",
        "public relations", "communications", "advertising", "google ads",
        "meta ads", "instagram", "tiktok", "linkedin", "customer engagement",
        "community management", "growth", "partnerships",
    ],

    "Finance and Accounting": [
        "finance", "accounting", "budgeting", "financial analysis",
        "financial reporting", "auditing", "audit", "tax", "bookkeeping",
        "accounts payable", "accounts receivable", "forecasting",
        "investment", "valuation", "cost analysis", "payroll",
        "financial modeling", "quickbooks", "erp", "invoicing",
        "reconciliation", "balance sheet", "income statement", "cash flow",
        "profit and loss", "p&l", "variance analysis",
    ],

    "Education and Training": [
        "teaching", "teacher", "training", "trainer", "curriculum",
        "lesson planning", "instructional design", "learning management system",
        "lms", "student support", "academic advising", "assessment",
        "e-learning", "online learning", "tutoring", "tutor",
        "classroom management", "learning outcomes", "education technology",
        "edtech", "workshop", "facilitation", "mentoring", "coaching",
        "course design", "student engagement", "educational content",
    ],

    "Healthcare and Science": [
        "healthcare", "patient care", "clinical", "laboratory", "lab",
        "research", "data collection", "medical", "pharmacy", "biology",
        "chemistry", "public health", "safety", "regulatory",
        "quality control", "scientific writing", "experiments", "analysis",
        "health", "nursing", "medical records", "diagnosis", "treatment",
        "healthcare administration", "clinical research",
    ],

    "Design and Product": [
        "ui", "ux", "user experience", "user interface", "figma", "adobe",
        "photoshop", "illustrator", "wireframing", "prototyping",
        "product management", "product design", "user research",
        "usability testing", "design thinking", "accessibility",
        "visual design", "graphic design", "interaction design",
        "customer journey", "roadmap", "product strategy", "mvp",
    ],

    "Human Resources": [
        "human resources", "hr", "recruitment", "recruiting", "talent",
        "talent acquisition", "onboarding", "employee relations",
        "performance management", "training coordination", "payroll",
        "benefits", "interview scheduling", "candidate screening",
        "job posting", "hr policies", "people operations",
    ],

    "Legal and Compliance": [
        "legal", "law", "contract", "contracts", "compliance", "policy",
        "regulation", "regulatory", "privacy", "data protection", "gdpr",
        "terms", "risk", "governance", "audit", "documentation",
        "case management", "legal research",
    ],

    "Soft Skills": [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "time management", "adaptability", "creativity",
        "attention to detail", "organization", "collaboration", "presentation",
        "negotiation", "decision making", "analytical thinking", "multitasking",
        "self motivated", "self-motivated", "independent", "fast learner",
        "professionalism", "interpersonal skills", "written communication",
        "verbal communication", "work under pressure", "prioritization",
        "ownership", "initiative", "curiosity", "reliability",
    ],

    "Common Qualifications": [
        "bachelor", "bachelor's", "degree", "diploma", "certification",
        "certificate", "internship", "intern", "graduate", "entry level",
        "entry-level", "fresh graduate", "student", "experience", "portfolio",
        "english", "arabic", "bilingual", "written", "verbal",
        "microsoft office", "word", "powerpoint", "outlook", "google workspace",
        "microsoft excel", "availability", "gpa", "major", "university",
    ],
}


# ── OpenAI client ─────────────────────────────────────────────────────────────

def _get_openai_client() -> OpenAI | None:
    """
    Return an OpenAI client if an API key is configured.

    Priority:
    1. Streamlit secrets
    2. Environment variable
    """
    try:
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    except Exception:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or not api_key.strip():
        return None

    return OpenAI(api_key=api_key)


# ── Prompt builder ────────────────────────────────────────────────────────────

def _build_prompt(job_description: str, company: str = "", job_title: str = "") -> str:
    """
    Build the prompt sent to OpenAI.
    """
    context = ""

    if company:
        context += f"Company: {company}\n"

    if job_title:
        context += f"Role: {job_title}\n"

    return f"""You are a career advisor helping a university student or fresh graduate prepare for a job application.

{context}
Job Description:
\"\"\"
{job_description[:3500]}
\"\"\"

Please analyze this job description and provide the following in a clear, structured format:

1. **Job Summary**
   - 2–3 sentences explaining the role in simple terms.

2. **Key Required Skills**
   - Bullet list of the top 6–8 skills or qualifications mentioned.

3. **Resume Keywords**
   - 10–12 keywords or phrases from the job description that the student can include in their resume.

4. **Interview Preparation Topics**
   - 4–6 likely interview questions or topic areas to prepare.

5. **Suggested Follow-up Email Draft**
   - A short, professional email to send after applying or interviewing.

6. **Practical Next Steps**
   - 3–4 concrete actions the student should take now.

Keep the tone practical, honest, and tailored for a student or early-career professional.
Do not guarantee hiring outcomes.
"""


# ── Main analyzer ─────────────────────────────────────────────────────────────

def analyze_job_description(
    job_description: str,
    company: str = "",
    job_title: str = "",
) -> dict:
    """
    Analyze a job description.

    Returns:
        dict with:
        - source: "openai", "fallback", or "error"
        - content: markdown-formatted analysis text
    """
    if not job_description or len(job_description.strip()) < 30:
        return {
            "source": "error",
            "content": "Please provide a more detailed job description of at least 30 characters.",
        }

    client = _get_openai_client()

    if client:
        return _ai_analysis(client, job_description, company, job_title)

    return _fallback_analysis(job_description, company, job_title)


def _ai_analysis(
    client: OpenAI,
    job_description: str,
    company: str,
    job_title: str,
) -> dict:
    """
    Call OpenAI API and return structured analysis.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful career advisor specializing in early-career "
                        "job seekers, especially university students and fresh graduates. "
                        "Provide clear, actionable, and honest advice. "
                        "Do not guarantee job offers or hiring outcomes."
                    ),
                },
                {
                    "role": "user",
                    "content": _build_prompt(job_description, company, job_title),
                },
            ],
            temperature=0.7,
            max_tokens=1200,
        )

        return {
            "source": "openai",
            "content": response.choices[0].message.content,
        }

    except Exception as e:
        st.warning(f"OpenAI API error: {e}. Falling back to rule-based analysis.")
        return _fallback_analysis(job_description, company, job_title)


# ── Rule-based fallback helpers ───────────────────────────────────────────────

def _extract_keywords_by_category(job_description: str) -> dict:
    """
    Extract matching keywords from the job description grouped by category.

    This is rule-based keyword matching, not generative AI.
    """
    text_lower = job_description.lower()
    matches = {}

    for category, keywords in SKILL_CATEGORIES.items():
        found = []

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Phrase-aware matching.
            # Example: "data analysis" should match as a phrase.
            pattern = r"(?<!\w)" + re.escape(keyword_lower) + r"(?!\w)"

            if re.search(pattern, text_lower):
                found.append(keyword)

        if found:
            # Remove duplicates while preserving order.
            matches[category] = list(dict.fromkeys(found))

    return matches


def _extract_important_lines(job_description: str) -> list:
    """
    Extract lines that look like requirements, responsibilities, or qualifications.
    """
    trigger_words = [
        "require", "required", "requirement", "requirements",
        "qualification", "qualifications", "qualified",
        "must", "should", "responsible", "responsibilities", "duties",
        "experience", "skills", "ability", "abilities", "knowledge",
        "proficient", "familiar", "preferred", "degree", "bachelor",
        "graduate", "excellent", "strong", "understanding", "support",
        "manage", "develop", "analyze", "coordinate", "communicate",
        "create", "design", "implement", "maintain", "prepare", "assist",
        "collaborate", "lead", "monitor", "evaluate", "deliver", "build",
        "write", "present", "report", "track", "research",
    ]

    lines = [
        line.strip(" -•\t")
        for line in job_description.split("\n")
        if line.strip()
    ]

    important_lines = []

    for line in lines:
        line_lower = line.lower()

        if any(word in line_lower for word in trigger_words):
            important_lines.append(line)

    # If the job description is written as one large paragraph,
    # split it into sentences and try again.
    if not important_lines:
        sentences = re.split(r"(?<=[.!?])\s+", job_description)

        important_lines = [
            sentence.strip()
            for sentence in sentences
            if any(word in sentence.lower() for word in trigger_words)
        ]

    # Remove duplicates and limit output.
    important_lines = list(dict.fromkeys(important_lines))

    return important_lines[:8]


def _guess_role_focus(keyword_matches: dict) -> str:
    """
    Guess the general focus area based on the strongest keyword category.
    """
    if not keyword_matches:
        return "general professional skills"

    strongest_category = max(
        keyword_matches,
        key=lambda category: len(keyword_matches[category])
    )

    focus_map = {
        "Technical Skills": "software, technical, or IT-related work",
        "Data and Analytics": "data, analytics, reporting, or insight generation",
        "Business and Operations": "business operations, coordination, or project support",
        "Marketing and Sales": "marketing, sales, communications, or customer growth",
        "Finance and Accounting": "finance, accounting, auditing, or business reporting",
        "Education and Training": "education, training, student support, or learning services",
        "Healthcare and Science": "healthcare, science, laboratory, or research support",
        "Design and Product": "design, product, user experience, or creative work",
        "Human Resources": "recruitment, employee support, or people operations",
        "Legal and Compliance": "legal, compliance, governance, or policy-related work",
        "Soft Skills": "communication, teamwork, and general workplace performance",
        "Common Qualifications": "entry-level qualifications and general employability",
    }

    return focus_map.get(strongest_category, "general professional skills")


def _format_detected_skills(keyword_matches: dict) -> str:
    """
    Format detected skill categories as markdown.
    """
    if not keyword_matches:
        return (
            "No specific keyword category was strongly detected. Focus on the role's "
            "main responsibilities, required qualifications, and transferable skills."
        )

    return "\n".join(
        f"- **{category}:** {', '.join(skills[:8])}"
        for category, skills in keyword_matches.items()
    )


def _get_resume_keywords(keyword_matches: dict) -> list:
    """
    Flatten detected keywords into a clean resume keyword list.
    """
    all_keywords = []

    for keywords in keyword_matches.values():
        all_keywords.extend(keywords)

    unique_keywords = list(dict.fromkeys(all_keywords))

    if not unique_keywords:
        unique_keywords = [
            "communication",
            "teamwork",
            "problem solving",
            "time management",
            "attention to detail",
            "adaptability",
            "organization",
            "professionalism",
        ]

    return unique_keywords[:15]


def _build_interview_topics(role_text: str, company_text: str, keyword_matches: dict) -> str:
    """
    Build interview preparation topics using detected categories.
    """
    base_topics = [
        f"Explain why you are interested in **{role_text}**{company_text}.",
        "Prepare one academic, internship, volunteer, or project example related to the role.",
        "Practice describing your strengths using clear examples.",
        "Prepare a STAR answer: Situation, Task, Action, Result.",
        "Prepare questions to ask the employer about the team, training, and expectations.",
    ]

    category_specific_topics = []

    if "Technical Skills" in keyword_matches:
        category_specific_topics.append(
            "Review the technical tools, programming languages, or platforms mentioned in the job description."
        )

    if "Data and Analytics" in keyword_matches:
        category_specific_topics.append(
            "Prepare to explain one example where you used data to solve a problem or make a decision."
        )

    if "Marketing and Sales" in keyword_matches:
        category_specific_topics.append(
            "Prepare to discuss a campaign, social media idea, customer insight, or sales-related example."
        )

    if "Finance and Accounting" in keyword_matches:
        category_specific_topics.append(
            "Review basic financial terms, reporting concepts, and any finance tools mentioned in the job post."
        )

    if "Education and Training" in keyword_matches:
        category_specific_topics.append(
            "Prepare to explain how you would support students, explain concepts, or improve learning outcomes."
        )

    if "Business and Operations" in keyword_matches:
        category_specific_topics.append(
            "Prepare to explain how you organize tasks, coordinate with others, and improve a process."
        )

    if "Design and Product" in keyword_matches:
        category_specific_topics.append(
            "Prepare to discuss your design process, portfolio, user research, or product-thinking examples."
        )

    final_topics = base_topics + category_specific_topics

    return "\n".join(f"- {topic}" for topic in final_topics[:8])


# ── Rule-based fallback analyzer ──────────────────────────────────────────────

def _fallback_analysis(
    job_description: str,
    company: str,
    job_title: str,
) -> dict:
    """
    Rule-based fallback analyzer.

    This does not use generative AI. It extracts common skills and important
    lines from the job description, then formats practical preparation guidance.
    """
    keyword_matches = _extract_keywords_by_category(job_description)
    important_lines = _extract_important_lines(job_description)
    role_focus = _guess_role_focus(keyword_matches)
    resume_keywords = _get_resume_keywords(keyword_matches)

    role_text = job_title.strip() if job_title else "this role"
    company_text = f" at {company.strip()}" if company else ""

    detected_skills_text = _format_detected_skills(keyword_matches)

    if important_lines:
        requirements_text = "\n".join(f"- {line}" for line in important_lines)
    else:
        requirements_text = (
            "- Review the job description carefully and identify repeated skills, "
            "tools, responsibilities, and qualifications."
        )

    interview_topics = _build_interview_topics(role_text, company_text, keyword_matches)

    content = f"""## Job Summary
The **{role_text}**{company_text} appears to focus on **{role_focus}**. Based on the job description, the candidate should connect their academic background, projects, internships, and transferable skills to the responsibilities of the role.

## Key Required Skills and Requirements
{requirements_text}

## Detected Skill Categories
{detected_skills_text}

## Resume Keywords
Include relevant keywords naturally in your resume, cover letter, and LinkedIn profile:

{', '.join(f'`{keyword}`' for keyword in resume_keywords)}

## Interview Preparation Topics
{interview_topics}

## Suggested Follow-up Email Draft
> Subject: Follow-up — {job_title or 'Job Application'}{f' at {company}' if company else ''}
>
> Dear Hiring Team,
>
> I hope you are doing well. I recently applied for the {job_title or 'position'}{f' at {company}' if company else ''} and wanted to express my continued interest in the opportunity.
>
> I am excited about the role because it aligns with my background, skills, and career goals. Please let me know if there is any additional information I can provide.
>
> Best regards,  
> [Your Name]

## Practical Next Steps
1. **Tailor your resume** — add the most relevant keywords from the job description.
2. **Prepare examples** — choose 2–3 projects, coursework examples, internships, or volunteer experiences that match the role.
3. **Research the organization** — review the company website, LinkedIn page, mission, services, and recent updates.
4. **Practice interview answers** — focus on motivation, teamwork, problem-solving, and role-specific skills.
5. **Check your application materials** — make sure your resume, LinkedIn profile, and email are professional and consistent.

---
*This analysis was generated by GradPath AI's rule-based assistant because no OpenAI API key is configured. It uses keyword matching and structured templates, not generative AI.*
"""

    return {
        "source": "fallback",
        "content": content,
    }
