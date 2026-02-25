from supabase import create_client
import os

def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise Exception("Supabase env vars not set")

    return create_client(url, key)