"""
validation.py
Validates application form inputs and returns user-friendly error messages.
"""

from datetime import date
from typing import Optional


def validate_application(
    company: str,
    job_title: str,
    job_type: str,
    application_date,
    status: str,
    priority: str,
    deadline=None,
    notes: str = "",
    job_description: str = "",
) -> list[str]:
    """
    Validates all fields for a job application.
    Returns a list of error messages (empty list means no errors).
    """
    errors = []

    # Required fields
    if not company or not company.strip():
        errors.append("Company name is required.")

    if not job_title or not job_title.strip():
        errors.append("Job title is required.")

    if not job_type:
        errors.append("Job type is required.")

    if not application_date:
        errors.append("Application date is required.")

    if not status:
        errors.append("Status is required.")

    if not priority:
        errors.append("Priority is required.")

    # Date logic
    if application_date and deadline:
        if deadline < application_date:
            errors.append("Deadline cannot be before the application date.")

    # Text length limits
    if notes and len(notes) > 500:
        errors.append(f"Notes must be 500 characters or fewer (currently {len(notes)}).")

    if job_description and len(job_description) > 4000:
        errors.append(
            f"Job description must be 4000 characters or fewer (currently {len(job_description)})."
        )

    return errors


def validate_search_query(query: str) -> str:
    """Sanitize a search query string."""
    return query.strip()[:200] if query else ""