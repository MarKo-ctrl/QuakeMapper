import geopandas as gpd  # pyright: ignore[reportMissingModuleSource]
from psycopg2.extras import execute_values  # pyright: ignore[reportMissingModuleSource]
from sqlalchemy import text

from .db import get_engine, get_psycopg2_connection

# ROLE: query and prepare data for analysis

engine = get_engine()
EXPECTED_ROW_COUNT = 175_000  # approximate USGS M4.5+ events, 2000-2025


def load_all():
    """
    Load full dataset.
    """
    query = """SELECT *
            FROM earthquakes"""
    return gpd.read_postgis(query, engine)


def load_magnitude_range(mag1: float, mag2: float):
    """
    Load events within a magnitude range.
    Return a GeoDataFrame
    """
    query = """SELECT *
            FROM earthquakes
            WHERE magnitude BETWEEN %(mag1)s AND %(mag2)s;"""
    return gpd.read_postgis(query, engine, params={"mag1": mag1, "mag2": mag2})


def load_by_year_range(year1: int, year2: int):
    """
    Load events between two years
    """
    query = """SELECT *
            FROM earthquakes
            WHERE year BETWEEN %(year1)s AND %(year2)s;"""
    return gpd.read_postgis(query, engine, params={"year1": year1, "year2": year2})


def load_by_bbox(min_lon, min_lat, max_lon, max_lat):
    """
    Load events within a bounding box
    """
    query = """SELECT id, year, month, magnitude, depth, tsunami, geom
            FROM earthquakes,
            (SELECT ST_MakeEnvelope(%(min_lon)s,%(min_lat)s,%(max_lon)s,%(max_lat)s, 4326) as bbox)
            WHERE ST_Within(geom, bbox);"""
    return gpd.read_postgis(
        query,
        engine,
        params={
            "min_lon": min_lon,
            "min_lat": min_lat,
            "max_lon": max_lon,
            "max_lat": max_lat,
        },
    )


def update_column(
    table_name: str, column_name: str, new_value, condition: str | None = None
):
    """
    Update a column in the database
    """
    conn = get_psycopg2_connection()
    query = f"""UPDATE {table_name}
            SET {column_name} = %(new_value)s
            {f"WHERE {condition}" if condition else ""};"""
    try:
        with conn.cursor() as cur:
            cur.execute(query, {"new_value": new_value})
        conn.commit()
        print(f"Column '{column_name}' updated in table '{table_name}'.")
    except Exception as e:
        print(f"Error updating column '{column_name}' in table '{table_name}': {e}")


def update_cluster_labels(gdf: gpd.GeoDataFrame, table_name: str, column_name: str):
    """
    Update table different values per row
    """
    pairs = list(zip(gdf[column_name], gdf["id"]))
    try:
        with get_psycopg2_connection() as conn:
            with conn.cursor() as cur:
                execute_values(
                    cur,
                    f"""UPDATE {table_name} SET {column_name} = data.val
                    FROM (VALUES %s) AS data (val, id)
                    WHERE {table_name}.id = data.id""",
                    pairs,
                )
            conn.commit()
        print(f"Cluster labels updated in table '{table_name}'.")
    except Exception as e:
        print(f"Error updating cluster labels in table '{table_name}': {e}")


def fetch_complete():
    with engine.connect() as conn:
        c = conn.execute(text("""SELECT COUNT(*) FROM earthquakes"""))
        return (c.scalar() or 0) > EXPECTED_ROW_COUNT


def cluster_complete():
    with engine.connect() as conn:
        # check that column cluster_id exists
        e = conn.execute(
            text("""SELECT EXISTS (SELECT 1 
            FROM information_schema.columns 
            WHERE table_schema='public'
                AND table_name='earthquakes'
                AND column_name='cluster_id');""")
        )
        column_exists = e.all()[0][0]

        if not column_exists:
            return False

        # check that cluster_id is not null
        nn = conn.execute(
            text("""SELECT COUNT(*) > 0
            FROM earthquakes
            WHERE cluster_id IS NOT NULL""")
        )
        return nn.all()[0][0]


def pct_events_within(distances: list[int] = [150_000, 300_000, 500_000]):
    pct_list = [{"distance": "", "total":"", "within":"", "pct":""} for _ in range(len(distances))]

    with engine.connect() as conn:
        total_events = conn.execute(text(
            """
            SELECT Count(*)
            FROM earthquakes e;"""
        )).scalar()

    for i, dist in enumerate(distances):
        with engine.connect() as conn:
            pct = conn.execute(
                text("""
                SELECT COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM plate_boundaries pb
                    WHERE ST_DWithin(pb.geom::geography, e.geom::geography, :d)
                    )) as within_dist,
                    ROUND(100.0 * COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM plate_boundaries pb
                    WHERE ST_DWithin(pb.geom::geography, e.geom::geography, :d)
                    )) / COUNT(*), 2)::float as pct_within_dist
                FROM earthquakes e;"""),
                {"d": dist},
            ).one()
            pct_list[i]["distance"] = dist
            pct_list[i]["total"] = total_events
            pct_list[i]["within"] = pct[0]
            pct_list[i]["pct"] = pct[1]
    return pct_list