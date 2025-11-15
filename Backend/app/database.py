import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DEFAULT_SQL_SERVER_CONFIG = {
    "driver": "ODBC Driver 18 for SQL Server",  # Hardcoded driver
    "host": "evokehackathonsqlserver.database.windows.net",  # Hardcoded host
    "port": "1433",  # Hardcoded port
    "database": "NeoCodeNexusDB",  # Hardcoded database
    "username": "NeoCodeNexusSQLUser",  # Hardcoded username
    "password": "cRVe8JttP12ccG03",  # Hardcoded password
}

default_connect_string = (
    f"DRIVER={{{DEFAULT_SQL_SERVER_CONFIG['driver']}}};"
    f"SERVER={DEFAULT_SQL_SERVER_CONFIG['host']},{DEFAULT_SQL_SERVER_CONFIG['port']};"
    f"DATABASE={DEFAULT_SQL_SERVER_CONFIG['database']};"
    f"UID={DEFAULT_SQL_SERVER_CONFIG['username']};"
    f"PWD={DEFAULT_SQL_SERVER_CONFIG['password']};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

print("Connection String:", default_connect_string)

SQLALCHEMY_DATABASE_URL = os.environ.get(
    "SQLALCHEMY_DATABASE_URL",
    f"mssql+pyodbc:///?odbc_connect={quote_plus(default_connect_string)}",
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

