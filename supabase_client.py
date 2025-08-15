import os
from flask import g
from werkzeug.local import LocalProxy
from supabase.client import Client, ClientOptions
from flask_storage import FlaskSessionStorage

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

def create_supabase_client(key: str) -> Client:
    return Client(
        SUPABASE_URL,
        key,
        options=ClientOptions(
            storage=FlaskSessionStorage(),
            flow_type="pkce"
        ),
    )

def get_supabase_anon() -> Client:
    if "supabase_anon" not in g:
        g.supabase_anon = create_supabase_client(SUPABASE_ANON_KEY)
    return g.supabase_anon

def get_supabase_service() -> Client:
    if "supabase_service" not in g:
        g.supabase_service = create_supabase_client(SUPABASE_SERVICE_ROLE_KEY)
    return g.supabase_service

# Proxies for easier access
supabase_anon: Client = LocalProxy(get_supabase_anon)
supabase_service: Client = LocalProxy(get_supabase_service)
