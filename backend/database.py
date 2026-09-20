import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# .env lives at the project root, one level up from this file. Resolving it
# from __file__ (this file's own location) instead of a relative path means
# it works no matter which directory you launch the server from.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def get_connection():
    # A single connection string (postgresql://user:password@host/dbname)
    # instead of separate host/user/password variables — the standard format
    # most cloud Postgres providers (Neon, Render, Supabase, ...) hand out.
    return psycopg.connect(os.environ["DATABASE_URL"])
