# api/test/conftest.py
import pytest
from api.database import get_db_connection
import pyodbc

@pytest.fixture(scope='module')
def memory_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérifier si la table existe déjà, sinon la créer
    cursor.execute("""
    IF OBJECT_ID('appmovieschema_User_Table', 'U') IS NULL
    CREATE TABLE appmovieschema_User_Table (
        user_id INTEGER PRIMARY KEY,
        pseudo TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    yield conn

    # Nettoyage après les tests
    cursor.execute("DROP TABLE appmovieschema_User_Table")
    conn.close()
