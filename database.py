"""
database.py
Handles Supabase client setup and connection.
"""

import os
import streamlit as st
from supabase import create_client, Client


def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client.
    Reads credentials from Streamlit secrets (production) or .env (local).
    """
    try:
        # Try Streamlit secrets first (for deployed app)
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variables (local dev)
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        st.error(
            "⚠️ Supabase credentials not found. "
            "Please set SUPABASE_URL and SUPABASE_KEY in your secrets or .env file."
        )
        st.stop()

    return create_client(url, key)


@st.cache_resource
def get_client() -> Client:
    """Cached Supabase client — created once per session."""
    return get_supabase_client()