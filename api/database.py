# database.py
import os
import pyodbc
import sqlite3
from dotenv import load_dotenv

load_dotenv()

server = os.getenv('DB_SERVER')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
driver = os.getenv('DB_DRIVER')
use_memory_db = os.getenv('USE_MEMORY_DB') == 'True'

def get_db_connection():
    if use_memory_db:
        # Utiliser SQLite en mémoire pour les tests
        conn = sqlite3.connect(':memory:')
        return conn
    else:
        # Connexion à la vraie base de données
        conn = pyodbc.connect(
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        return conn
