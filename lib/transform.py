import pandas as pd
import geopandas as gpd
from. import extract

def text2df(filename: str, _crs: str):
    """
    Convert a text file into a GeoDataFrame containing geographical data.

    This function reads a text file specified by the filename and extracts 
    information such as date, time, depth, magnitude, and geographic coordinates.
    It organizes the extracted data into a dictionary and then constructs 
    a GeoDataFrame using GeoPandas with the given coordinate reference system.

    Args:
        filename (str): The path to the text file containing geological data.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing geological data including
                          'Date', 'Time(GMT)', 'Depth(km)', 'Magnitude(Local)', 
                          and 'geometry' as Point objects. 

    Example:
        >>> df = text2df("data.txt", "EPSG:4326")
        >>> print(df.head())
    """
    with open(filename, 'r', encoding='UTF-8') as f:
        lines = '\n'.join(f.readlines())
        d = {'Date': extract.to_date(lines),
             'Time(GMT)': extract.to_time(lines),
             'Depth(km)': extract.to_depth(lines),
             'Magnitude(Local)': extract.to_magnitude(lines),
             'geometry': extract.create_points(lines)}
        gdf = gpd.GeoDataFrame(d, crs = _crs)
    # set the date as the dataframe index
    gdf['Date'] = pd.to_datetime(gdf['Date'], dayfirst=True)
    gdf = gdf.set_index('Date')
    # separate column for month
    gdf['Month'] = gdf.index.month_name()
    return gdf

def combine_df(lst_df: list):
    return pd.concat(lst_df, ignore_index = True)

def reproject(gdf, _crs: int):
    return gdf.to_crs(epsg = _crs)

def clip_gdf(gdf, mask_path, _crs: int):
    m = gpd.GeoSeries.from_file(mask_path)
    return (mask := m.to_crs(epsg = _crs)), gpd.clip(gdf, mask)


def gdf_info(gdf):
    print(f"Rows:{gdf.shape[0]}, Columns:{gdf.shape[1]}")
    print(gdf.head())
    print(gdf.tail(),'\n\n')