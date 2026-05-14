import os
import psycopg2
from psycopg2 import sql, errors
from dotenv import load_dotenv

load_dotenv()
DB_NAME = "quakemapper"

def _get_conn_params(dbname="marko_db"):
    return dict(
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", 5432)),
        user=os.environ.get("PGUSER", "postgres"),
        dbname=dbname,
        # no password — libpq reads ~/.pgpass automatically
    )

def create_database():
    conn = psycopg2.connect(**_get_conn_params())
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME))
            )
        print(f"Database '{DB_NAME}' created.")
    except errors.DuplicateDatabase:
        print(f"Database '{DB_NAME}' already exists, skipping.")
    finally:
        conn.close()

def enable_postgis():
    conn = psycopg2.connect(**_get_conn_params(dbname=DB_NAME))
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        conn.commit()
        print("PostGIS extension enabled.")
    finally:
        conn.close()

def setup():
    create_database()
    enable_postgis()

if __name__ == "__main__":
    setup()