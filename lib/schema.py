import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "quakemapper"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS earthquakes (
    id          VARCHAR(20) PRIMARY KEY,
    time        TIMESTAMP WITH TIME ZONE NOT NULL,
    year        SMALLINT NOT NULL,
    month       SMALLINT NOT NULL,
    magnitude   NUMERIC(4,2) NOT NULL,
    mag_type    VARCHAR(10),
    depth       NUMERIC(7,3) NOT NULL,
    place       TEXT,
    status      VARCHAR(20),
    tsunami     SMALLINT,
    sig         INTEGER,
    geom        GEOMETRY(POINT, 4326) NOT NULL
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_earthquakes_geom ON earthquakes USING GIST(geom);",
    "CREATE INDEX IF NOT EXISTS idx_earthquakes_time ON earthquakes (time);",
    "CREATE INDEX IF NOT EXISTS idx_earthquakes_year_month ON earthquakes (year, month);",
]


def create_schema():
    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "/var/run/postgresql"),
        port=int(os.environ.get("PGPORT", 5432)),
        user=os.environ.get("PGUSER", "marko"),
        dbname=DB_NAME,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE)
            for idx in CREATE_INDEXES:
                cur.execute(idx)
        conn.commit()
        print("Table and indexes created.")
    finally:
        conn.close()


if __name__ == "__main__":
    create_schema()
