# dbenv.py
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

DB_CONFIG: Dict[str, Any] = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "openvpn"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", ""),
}

def get_db_connection() -> connection:
    return psycopg2.connect(**DB_CONFIG)