"""
applications.py
CRUD functions for the `applications` table in Supabase.
"""

from datetime import date
from typing import Optional
import streamlit as st
import pandas as pd
from database import get_client


# ── Constants ──────────────────────────────────────────────────────────────────

STATUS_OPTIONS = ["Saved", "Applied", "Interview", "Offer", "Rejected"]
PRIORITY_OPTIONS = ["Low", "Medium", "High"]
JOB_TYPE_OPTIONS = ["Internship", "Part-time", "Full-time", "Graduate Program"]
SOURCE_OPTIONS = [
    "LinkedIn",
    "University Portal",
    "Career Fair",
    "Company Website",
    "Referral",
    "Other",
]


# ── Create ─────────────────────────────────────────────────────────────────────

def create_application(data: dict) -> dict | None:
    """
    Insert a new application into Supabase.
    `data` should match the applications table schema.
    Returns the inserted row or None on failure.
    """
    client = get_client()
    try:
        # Convert date objects to ISO strings for JSON serialization
        payload = _serialize_dates(data)
        response = client.table("applications").insert(payload).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error saving application: {e}")
        return None


# ── Read ───────────────────────────────────────────────────────────────────────

def get_all_applications() -> pd.DataFrame:
    """
    Fetch all applications from Supabase, ordered by application_date descending.
    Returns a pandas DataFrame (empty DataFrame if none found).
    """
    client = get_client()
    try:
        response = (
            client.table("applications")
            .select("*")
            .order("application_date", desc=True)
            .execute()
        )
        if response.data:
            df = pd.DataFrame(response.data)
            # Parse date columns
            for col in ["application_date", "deadline", "created_at", "updated_at"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching applications: {e}")
        return pd.DataFrame()


def get_application_by_id(app_id: int) -> dict | None:
    """Fetch a single application by its primary key."""
    client = get_client()
    try:
        response = (
            client.table("applications")
            .select("*")
            .eq("id", app_id)
            .single()
            .execute()
        )
        return response.data
    except Exception as e:
        st.error(f"Error fetching application: {e}")
        return None


# ── Update ─────────────────────────────────────────────────────────────────────

def update_application(app_id: int, data: dict) -> bool:
    """
    Update an existing application by ID.
    Returns True on success, False on failure.
    """
    client = get_client()
    try:
        payload = _serialize_dates(data)
        # Always refresh updated_at
        payload["updated_at"] = "now()"
        response = (
            client.table("applications")
            .update(payload)
            .eq("id", app_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        st.error(f"Error updating application: {e}")
        return False


# ── Delete ─────────────────────────────────────────────────────────────────────

def delete_application(app_id: int) -> bool:
    """
    Delete an application by ID.
    Returns True on success, False on failure.
    """
    client = get_client()
    try:
        response = (
            client.table("applications")
            .delete()
            .eq("id", app_id)
            .execute()
        )
        return True
    except Exception as e:
        st.error(f"Error deleting application: {e}")
        return False


# ── Search / Filter helpers ────────────────────────────────────────────────────

def filter_applications(
    df: pd.DataFrame,
    search_query: str = "",
    status_filter: list[str] | None = None,
    job_type_filter: list[str] | None = None,
    priority_filter: list[str] | None = None,
    sort_by: str = "application_date",
    sort_asc: bool = False,
) -> pd.DataFrame:
    """
    Apply search, filter, and sort operations to an applications DataFrame.
    All filtering is done client-side to avoid extra round-trips to Supabase.
    """
    if df.empty:
        return df

    filtered = df.copy()

    # Search
    if search_query:
        q = search_query.lower()
        mask = (
            filtered["company"].str.lower().str.contains(q, na=False)
            | filtered["job_title"].str.lower().str.contains(q, na=False)
            | filtered["source"].str.lower().str.contains(q, na=False)
        )
        filtered = filtered[mask]

    # Status filter
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]

    # Job type filter
    if job_type_filter:
        filtered = filtered[filtered["job_type"].isin(job_type_filter)]

    # Priority filter
    if priority_filter:
        filtered = filtered[filtered["priority"].isin(priority_filter)]

    # Sort
    if sort_by in filtered.columns:
        try:
            filtered = filtered.sort_values(sort_by, ascending=sort_asc, na_position="last")
        except Exception:
            pass

    return filtered.reset_index(drop=True)


# ── Internal helpers ───────────────────────────────────────────────────────────

def _serialize_dates(data: dict) -> dict:
    """Convert date/datetime objects to ISO format strings for JSON."""
    result = {}
    for k, v in data.items():
        if isinstance(v, date):
            result[k] = v.isoformat()
        else:
            result[k] = v
    return result