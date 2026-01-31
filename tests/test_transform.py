import pytest
import pandas as pd
import geopandas as gpd
from shapely import Point
from ..lib.transform import text2df, combine_df, reproject, clip_gdf, gdf_info, export2geojson

sample_text = """
DATE         TIME     LAT.   LONG.  DEPTH    MAGNITUDE
                    (GMT)    (N)    (E)    (km)       (Local)
2021 JAN  1   00 38 24.3 38.3894 21.9832    8         1.2
"""

def test_text2df(tmp_path):
    # Create a temporary file with the sample text
    file_path = tmp_path / "sample.txt"
    file_path.write_text(sample_text)
    gdf = text2df(str(file_path), "EPSG:4326")
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf.index.name == 'Date'  # The function sets the index to 'Date'
    assert len(gdf) == 1
    assert gdf.crs == "EPSG:4326"

def test_combine_df():
    df1 = pd.DataFrame({'A': [1]})
    df2 = pd.DataFrame({'A': [2]})
    combined = combine_df([df1, df2])
    assert len(combined) == 2

def test_reproject():
    gdf = gpd.GeoDataFrame({'geometry': [Point(21.9832, 38.3894)]}, crs="EPSG:4326")
    reprojected = reproject(gdf, 3857)
    assert reprojected.crs == "EPSG:3857"

@pytest.fixture
def sample_gdf():
    return gpd.GeoDataFrame({'geometry': [Point(21.9832, 38.3894)]}, crs="EPSG:4326")

def test_clip_gdf(sample_gdf, tmp_path):
    # Create a mock mask GeoJSON
    mask_path = tmp_path / "mask.geojson"
    mask_gdf = gpd.GeoDataFrame({'geometry': [Point(21.9832, 38.3894).buffer(1)]}, crs="EPSG:3857")
    mask_gdf.to_file(mask_path, driver='GeoJSON')
    mask, clipped = clip_gdf(sample_gdf, str(mask_path), 3857)
    assert isinstance(mask, gpd.GeoSeries)
    assert isinstance(clipped, gpd.GeoDataFrame)

def test_gdf_info(sample_gdf, capsys):
    gdf_info(sample_gdf)
    captured = capsys.readouterr()
    assert 'Rows:1' in captured.out

def test_export2geojson(sample_gdf, tmp_path):
    path = tmp_path / "test.geojson"
    export2geojson(sample_gdf, str(path))
    assert path.exists()