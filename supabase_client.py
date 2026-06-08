import os
import streamlit as st
from supabase import create_client, Client


class SupabaseConfigError(Exception):
    pass


@st.cache_resource
def get_supabase_client() -> Client:
    """Create a cached Supabase client using Streamlit Secrets or environment variables."""
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

    if not url or not key:
        raise SupabaseConfigError(
            "Faltan SUPABASE_URL o SUPABASE_KEY en Streamlit Secrets."
        )

    return create_client(url, key)
