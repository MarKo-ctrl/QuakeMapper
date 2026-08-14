import calendar
import logging
from datetime import date, datetime, timezone

import geopandas as gpd
import requests
import shapely
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    Numeric,
    SmallInteger,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .db import get_engine
from .db_queries import table_exists_complete

engine = get_engine()

logging.basicConfig(
    filename="logs/info_insert.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

USGS_BASE = "https://earthquake.usgs.gov/fdsnws/event/1/query"

_meta = MetaData()
_earthquakes = Table(
    "earthquakes",
    _meta,
    Column("id", String(20), primary_key=True),
    Column("time", PG_TIMESTAMP(timezone=True), nullable=False),
    Column("year", SmallInteger, nullable=False),
    Column("month", SmallInteger, nullable=False),
    Column("magnitude", Numeric(4, 2), nullable=False),
    Column("mag_type", String(10)),
    Column("depth", Numeric(7, 3), nullable=False),
    Column("place", Text),
    Column("status", String(20)),
    Column("tsunami", SmallInteger),
    Column("sig", Integer),
    Column("geom", Geometry("POINT", srid=4326), nullable=False),
)


def generate_date_ranges(start_yr=2000, end_yr=2026) -> list[tuple[date, date]]:
    """
    Returns a list of (start, end) tuples for
    every month for years 2000 to 2025
    """
    ranges = []
    for year in range(start_yr, end_yr):
        for month in range(1, 13):
            start = date(year, month, 1)
            end = date(year, month, calendar.monthrange(year, month)[1])
            ranges.append((start, end))
    return ranges


def build_url(start: date, end: date) -> str:
    """
    Constructs the USGS query URL from a start / end
    date pair.
    """
    return (
        f"{USGS_BASE}?format=geojson"
        f"&starttime={start}&endtime={end}"
        f"&minmagnitude=4.5"
        f"&orderby=time-asc"
    )


def parse_feature(feature: dict) -> dict:
    """
    Parses a single GeoJSON featue into a flat dictionary
    matching the database schema.
    """
    props = feature["properties"]
    lon, lat, depth = feature["geometry"]["coordinates"]
    dt = datetime.fromtimestamp(props["time"] / 1000, tz=timezone.utc)

    if props["mag"] is None:
        logger.warning(f"{feature['id']}, {dt.year}, {dt.month} - null magnitude")
        # return None

    if len(feature["id"]) > 20:
        logger.warning(f"Long ID found: {feature['id']} ({len(feature['id'])} chars)")

    return {
        "id": feature["id"],
        "time": dt,
        "year": dt.year,
        "month": dt.month,
        "magnitude": props.get("mag"),
        "mag_type": props.get("magType"),
        "depth": depth,
        "place": props.get("place"),
        "status": props.get("status"),
        "tsunami": props.get("tsunami"),
        "sig": props.get("sig"),
        "geom": WKTElement(f"POINT({lon} {lat})", srid=4326),
    }


def fetch_chunk(start: date, end: date) -> list[dict]:
    """
    Fetches one month's data from USGS,
    returns a list of parsed event dictionaries.
    """
    url = build_url(start, end)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return [parse_feature(f) for f in response.json().get("features", [])]


def month_exists(engine, year: int, month: int) -> bool:
    """
    Checks the database whether a given
    year/month already has data.
    """
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM earthquakes WHERE year = :y AND month = :m LIMIT 1"),
            {"y": year, "m": month},
        )
        return result.fetchone() is not None


def insert_chunk(engine, records: list[dict]) -> None:
    """
    Inserts a list of parsed event dictionaries
    into PostGIS.
    """
    if not records:
        return
    stmt = pg_insert(_earthquakes).on_conflict_do_nothing(index_elements=["id"])
    with engine.begin() as conn:
        conn.execute(stmt, records)


def fetch_all(start_yr: int, end_yr: int) -> None:
    """
    Orchastrates the full pipeline;
    iterates date ranges, skip existing months,
    fetches and inserts.
    """
    for start, end in generate_date_ranges(start_yr, end_yr):
        if month_exists(engine, start.year, start.month):
            logger.info(f"{start.year}-{start.month:02d}: already loaded, skipping.")
            continue

        logger.info(f"{start.year}-{start.month:02d}: fetching ...")

        records = fetch_chunk(start, end)
        insert_chunk(engine, records)

        logger.info(f"{len(records)} events inserted.")

def multi_poly(geom):
    if geom.geom_type == 'Polygon':
        return shapely.MultiPolygon([geom])
    else:
        return geom

def geojson_to_postgis(filepath: str, tablename: str):
    gdf = gpd.GeoDataFrame.from_file(filepath)
    gdf["geometry"] = gdf["geometry"].apply(multi_poly)

    if table_exists_complete(tablename):
        print("Table exists!")
    else:
        gdf.to_postgis(name=tablename,
                   con=engine,
                   if_exists="replace",
                   dtype={"geometry":Geometry("MULTIPOLYGON", srid=4326)})