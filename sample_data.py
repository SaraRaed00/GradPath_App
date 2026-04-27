"""
sample_data.py
Inserts realistic demo applications into Supabase for presentation purposes.
Run this manually from the Streamlit UI (sidebar button) or directly via:
    python sample_data.py
"""

from datetime import date, timedelta
from applications import create_application

SAMPLE_APPLICATIONS = [
    {
        "company": "Google",
        "job_title": "Software Engineering Intern",
        "job_type": "Internship",
        "location": "Mountain View, CA (Hybrid)",
        "application_date": date.today() - timedelta(days=30),
        "deadline": date.today() - timedelta(days=35),
        "status": "Interview",
        "priority": "High",
        "source": "LinkedIn",
        "job_description": "Join Google's SWE internship program. You will work on real products impacting billions of users. Requirements: strong CS fundamentals, Python or Java, data structures & algorithms.",
        "notes": "Phone screen passed. Technical interview scheduled for next week.",
    },
    {
        "company": "McKinsey & Company",
        "job_title": "Business Analyst",
        "job_type": "Full-time",
        "location": "Dubai, UAE",
        "application_date": date.today() - timedelta(days=25),
        "deadline": date.today() + timedelta(days=5),
        "status": "Applied",
        "priority": "High",
        "source": "University Portal",
        "job_description": "McKinsey seeks analytically-minded graduates to join our consulting team. Strong academic record required, excellent communication skills, problem solving.",
        "notes": "Applied via the university careers portal. Waiting for response.",
    },
    {
        "company": "Noon",
        "job_title": "Data Science Intern",
        "job_type": "Internship",
        "location": "Dubai, UAE",
        "application_date": date.today() - timedelta(days=20),
        "deadline": date.today() + timedelta(days=10),
        "status": "Applied",
        "priority": "Medium",
        "source": "LinkedIn",
        "job_description": "Work with the data team to build ML models for our e-commerce platform. Skills: Python, pandas, scikit-learn, SQL.",
        "notes": "",
    },
    {
        "company": "Careem",
        "job_title": "Product Manager — Intern",
        "job_type": "Internship",
        "location": "Dubai, UAE (Remote)",
        "application_date": date.today() - timedelta(days=15),
        "deadline": date.today() + timedelta(days=3),
        "status": "Interview",
        "priority": "High",
        "source": "Referral",
        "job_description": "Support PM team in planning and prioritizing product features for Careem's super-app platform. Strong analytical and communication skills needed.",
        "notes": "Friend referred me. Had a coffee chat with the hiring manager.",
    },
    {
        "company": "Amazon",
        "job_title": "Cloud Support Associate",
        "job_type": "Full-time",
        "location": "Remote",
        "application_date": date.today() - timedelta(days=45),
        "deadline": date.today() - timedelta(days=40),
        "status": "Rejected",
        "priority": "Medium",
        "source": "Company Website",
        "job_description": "AWS Cloud Support role. Linux, networking, troubleshooting experience preferred.",
        "notes": "Got generic rejection email after 3 weeks.",
    },
    {
        "company": "MIT — EECS",
        "job_title": "MSc Computer Science",
        "job_type": "Graduate Program",
        "location": "Cambridge, MA",
        "application_date": date.today() - timedelta(days=60),
        "deadline": date.today() - timedelta(days=30),
        "status": "Applied",
        "priority": "High",
        "source": "University Portal",
        "job_description": "Graduate program in EECS. Research areas: AI, systems, theory. GRE required. Letters of recommendation required.",
        "notes": "Submitted all materials. Awaiting decision.",
    },
    {
        "company": "Talabat",
        "job_title": "Backend Engineer — Graduate",
        "job_type": "Full-time",
        "location": "Dubai, UAE",
        "application_date": date.today() - timedelta(days=10),
        "deadline": date.today() + timedelta(days=14),
        "status": "Saved",
        "priority": "Medium",
        "source": "LinkedIn",
        "job_description": "Building scalable microservices with Go and Kubernetes. Experience with distributed systems a plus.",
        "notes": "Still need to tailor resume before applying.",
    },
    {
        "company": "Emirates NBD",
        "job_title": "Technology Graduate Program",
        "job_type": "Graduate Program",
        "location": "Dubai, UAE",
        "application_date": date.today() - timedelta(days=5),
        "deadline": date.today() + timedelta(days=20),
        "status": "Applied",
        "priority": "Medium",
        "source": "Career Fair",
        "job_description": "2-year rotational tech graduate program. Rotations across digital banking, cybersecurity, and data analytics.",
        "notes": "Met recruiter at university career fair.",
    },
    {
        "company": "Spotify",
        "job_title": "Machine Learning Engineer Intern",
        "job_type": "Internship",
        "location": "Stockholm, Sweden (Hybrid)",
        "application_date": date.today() - timedelta(days=8),
        "deadline": date.today() + timedelta(days=2),
        "status": "Applied",
        "priority": "High",
        "source": "Company Website",
        "job_description": "Work on Spotify's recommendation systems. PyTorch, TensorFlow, large-scale data pipelines. Must be comfortable with A/B testing.",
        "notes": "Deadline very soon! Need to follow up.",
    },
    {
        "company": "PwC",
        "job_title": "Technology Consulting Intern",
        "job_type": "Internship",
        "location": "Abu Dhabi, UAE",
        "application_date": date.today() - timedelta(days=50),
        "deadline": date.today() - timedelta(days=45),
        "status": "Offer",
        "priority": "Medium",
        "source": "Career Fair",
        "job_description": "Technology consulting internship. Work with clients on digital transformation projects. Excel, PowerPoint, communication skills required.",
        "notes": "Received offer! Considering alongside Careem.",
    },
]


def insert_one_sample_application() -> tuple[bool, str]:
    """
    Insert one sample application into Supabase.

    This function avoids duplicates by checking company + job_title.
    Returns:
        (True, message) if one sample was inserted
        (False, message) if all samples already exist or insertion failed
    """
    from applications import get_all_applications

    existing_df = get_all_applications()

    existing_pairs = set()

    if not existing_df.empty:
        for _, row in existing_df.iterrows():
            existing_pairs.add(
                (
                    str(row.get("company", "")).strip().lower(),
                    str(row.get("job_title", "")).strip().lower(),
                )
            )

    for app in SAMPLE_APPLICATIONS:
        pair = (
            app["company"].strip().lower(),
            app["job_title"].strip().lower(),
        )

        if pair not in existing_pairs:
            result = create_application(app)

            if result:
                return True, f"Inserted sample application: {app['company']} — {app['job_title']}"

            return False, "Tried to insert a sample application, but the database insert failed."

    return False, "All sample applications already exist. No new sample was inserted."


if __name__ == "__main__":
    success, message = insert_one_sample_application()
    print(message)