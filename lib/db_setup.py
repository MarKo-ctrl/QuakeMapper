from psycopg2 import errors, sql

from .db import get_psycopg2_connection

DB_NAME = "quakemapper"

def create_database():
    conn = get_psycopg2_connection(dbname="marko_db")
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
    conn = get_psycopg2_connection()
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


def add_table_column(table_name: str, column_name: str, data_type: str):
    query = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {data_type};"
    with get_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()
        print(f"Column '{column_name}' ensured on table '{table_name}'.")


if __name__ == "__main__":
    setup()