import os

import psycopg
from dotenv import load_dotenv

# .env lives at the project root, one level up from backend/
load_dotenv(dotenv_path="../.env")


def get_connection():
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
