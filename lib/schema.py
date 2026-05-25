from .db import get_psycopg2_connection

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS earthquakes (
    id          VARCHAR(50) PRIMARY KEY,
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
    conn = get_psycopg2_connection()
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
