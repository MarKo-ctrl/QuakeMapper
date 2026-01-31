import pytest
from ..lib.extract import to_date, to_time, to_latitude, to_longitude, to_depth, to_magnitude, create_points

# Sample text mimicking the data file format
sample_text = """
DATE         TIME     LAT.   LONG.  DEPTH    MAGNITUDE            
                    (GMT)    (N)    (E)    (km)       (Local)
2021 JAN  1   00 38 24.3 38.3894 21.9832    8         1.2
2021 FEB 15   14 30 59.1 40.7128 25.3047  100        5.8
"""

def test_to_date():
    dates = to_date(sample_text)
    assert dates == ['01/01/2021', '15/02/2021']

def test_to_time():
    times = to_time(sample_text)
    assert times == ['00:38:24.300000', '14:30:59.100000']

def test_to_latitude():
    lats = to_latitude(sample_text)
    assert lats == [38.3894, 40.7128]

def test_to_longitude():
    lons = to_longitude(sample_text)
    assert lons == [21.9832, 25.3047]

def test_to_depth():
    depths = to_depth(sample_text)
    assert depths == [8, 100]

def test_to_magnitude():
    mags = to_magnitude(sample_text)
    assert mags == [1.2, 5.8]

def test_create_points():
    points = create_points(sample_text)
    assert len(points) == 2
    assert str(points[0]) == 'POINT (21.9832 38.3894)'  # shapely Point format