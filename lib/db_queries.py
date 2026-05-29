# import pandas as pd
import geopandas as gpd

# from . import extract
from .db import get_engine

# ROLE: query and prepare data for analysis

engine = get_engine()

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
