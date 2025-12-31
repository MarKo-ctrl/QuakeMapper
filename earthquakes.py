from lib import get_data

import re
from datetime import datetime

# geodataframe
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# plot
import matplotlib.pyplot as plt
import contextily as cx

years = [2021, 2022]
get_data.get_earthquakes(years)


## Data Cleaning
def to_date(text):
    """
    Convert date strings from a specific format found within a given text.

    This function scans the input text for date patterns that match 
    the format 'YYYY MMM DD', where 'YYYY' is a 4-digit year, 'MMM' 
    is a 3-letter month abbreviation (in uppercase), and 'DD' 
    is the 1 or 2-digit day of the month. It extracts any matching 
    dates and returns them in the 'DD/MM/YYYY' format.

    Args:
        text (str): The input text containing potential date strings.

    Returns:
        list: A list of strings representing the dates found, formatted as 'DD/MM/YYYY'.
        If no valid dates are found, an empty list is returned.
    
    Example:
        >>> to_date("The event is planned for 2025 MAR 15 and 2026 APR 02.")
        ['15/03/2025', '02/04/2026']
    """
    date_re = re.compile(r'(\d{4}\s+[A-Z]{3}\s+\d{1,2})')
    dates =  date_re.findall(text)
    return [datetime.strptime(d, '%Y %b %d').strftime('%d/%m/%Y') for d in dates]

def to_time(text):
    """
    Convert time strings from a specific format found within a given text.

    This function scans the input text for time patterns that match 
    the format 'HH MM SS.ssssss', where 'HH' is the 2-digit hour (24-hour format), 
    'MM' is the 2-digit minute, and 'SS.ssssss' represents the seconds 
    which may include a fractional part. It extracts any matching times 
    and returns them in the 'HH:MM:SS.ssssss' format.

    Args:
        text (str): The input text containing potential time strings.

    Returns:
        list: A list of strings representing the times found, formatted as 'HH:MM:SS.ssssss'.
              If no valid times are found, an empty list is returned.

    Example:
        >>> to_time("The event starts at 14 30 59.123456 and ends at 15 45 50.654321.")
        ['14:30:59.123456', '15:45:50.654321']
    """
    time_re = re.compile(r'\d{2}\s{1}\d{2}\s{1}[\d.]+')
    times = time_re.findall(text)
    return [datetime.strptime(t, '%H %M %S.%f').strftime('%H:%M:%S.%f') for t in times]

def to_latitude(text):
    """
    Extract latitude values from a given text string.

    This function scans the input text for patterns representing latitude values 
    that appear before a corresponding longitude value. A latitude value is defined 
    as a decimal number that is followed by a space and another decimal number, 
    which represents longitude. It extracts any matching latitude values and 
    returns them as a list of floats.

    Args:
        text (str): The input text containing potential latitude values.

    Returns:
        list: A list of floats representing the latitudes found in the text.
              If no valid latitudes are found, an empty list is returned.

    Example:
        >>> to_latitude("The coordinates are 34.0522 -118.2437 and 40.7128 -74.0060.")
        [34.0522, 40.7128]
    """
    lat_re = re.compile(r'([\d.]+)(?=\s[\d.]+\s{2,4})', flags = re.MULTILINE)
    lats = lat_re.findall(text)
    return [float(lat) for lat in lats]

def to_longitude(text):
    """
    Extract longitude values from a given text string.

    This function scans the input text for patterns representing longitude values 
    that appear after a corresponding latitude value. A longitude value is defined 
    as a decimal number that follows a specific spacing pattern indicating latitude. 
    It extracts any matching longitude values and returns them as a list of floats.

    Args:
        text (str): The input text containing potential longitude values.

    Returns:
        list: A list of floats representing the longitudes found in the text.
              If no valid longitudes are found, an empty list is returned.

    Example:
        >>> to_longitude("The coordinates are 34.0522 -118.2437 and 40.7128 -74.0060.")
        [-118.2437, -74.0060]
    """
    lon_re = re.compile(r'([\d.]+)(?=\s{2,}\d+\s{2,}[\d.]+$)', flags = re.MULTILINE)
    lons = lon_re.findall(text)
    return [float(lon) for lon in lons]

def to_depth(text):
    """
    Extract depth values from a given text string.

    This function scans the input text for patterns representing depth values 
    that appear before a corresponding measurement or data point. A depth value 
    is defined as a whole number that is followed by a specific spacing pattern 
    indicating additional information. It extracts any matching depth values and 
    returns them as a list of integers.

    Args:
        text (str): The input text containing potential depth values.

    Returns:
        list: A list of integers representing the depths found in the text.
              If no valid depths are found, an empty list is returned.

    Example:
        >>> to_depth("The measurements are 100     23.5 and 200     45.6.")
        [100, 200]
    """
    depth_re = re.compile(r'(\d+)(?=\s{5,}[\d.])')
    depths = depth_re.findall(text)
    return [int(depth) for depth in depths]

def to_magnitude(text):
    """
    Extract magnitude values from a given text string.

    This function scans the input text for patterns representing magnitude values 
    that are located at the end of lines. A magnitude value is defined as a decimal 
    number. It extracts any matching magnitude values and returns them as a list of floats.

    Args:
        text (str): The input text containing potential magnitude values.

    Returns:
        list: A list of floats representing the magnitudes found in the text.
              If no valid magnitudes are found, an empty list is returned.

    Example:
        >>> to_magnitude("Event 1: 5.8\nEvent 2: 6.3\nEvent 3: 4.5")
        [5.8, 6.3, 4.5]
    """
    magn_re = re.compile(r'([\d.]+)$', flags=re.MULTILINE)
    magns = magn_re.findall(text)
    return [float(m) for m in magns]

def create_points(lst):
    """
    Create a list of Point objects from latitude and longitude values in the input list.

    This function takes a list of strings, extracts longitude and latitude values 
    by joining the list into a single string, and then converts them to Point objects. 
    It assumes that the input list contains valid latitude and longitude pairs in 
    a compatible format.

    Args:
        lst (list of str): A list containing strings from which latitude and 
                           longitude values will be extracted.

    Returns:
        list: A list of Point objects created from the extracted latitude and 
              longitude values. If there are mismatched counts of latitudes and 
              longitudes, it may cause an index error.

    Example:
        >>> create_points(["34.0522 -118.2437", "40.7128 -74.0060"])
        [Point(-118.2437, 34.0522), Point(-74.0060, 40.7128)]
    """
    lon = to_longitude(''.join(lst))
    lat = to_latitude(''.join(lst))
    return [Point(lon[i], lat[i]) for i in range(len(lon))]

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
        d = {'Date': to_date(lines),
             'Time(GMT)': to_time(lines),
             'Depth(km)': to_depth(lines),
             'Magnitude(Local)': to_magnitude(lines),
             'geometry': create_points(lines)}
        return gpd.GeoDataFrame(d, crs = _crs)

# from text lines to pandas (Geo)DataFrame...
eques_gdf_2021 = text2df('Data/CAT2021.TXT')
eques_gdf_2022 = text2df('Data/CAT2022.TXT')

eques_gdf_2021.head()
eques_gdf_2021.tail()
print(f"rows:{eques_gdf_2021.shape[0]}, columns:{eques_gdf_2021.shape[1]}")

eques_gdf_2022.head()
eques_gdf_2022.tail()
print(f"rows:{eques_gdf_2021.shape[0]}, columns:{eques_gdf_2022.shape[1]}")

# combine earthquakes data frames
eques_gdf = pd.concat([eques_gdf_2021, eques_gdf_2022], ignore_index = True)
eques_gdf.shape

eques_wm = eques_gdf.to_crs(epsg = 3857)

# set the date as the dataframe index
eques_wm['Date'] = pd.to_datetime(eques_wm['Date'], dayfirst=True)
eques_wm = eques_wm.set_index('Date')

# separate column for month
eques_wm['Month'] = eques_wm.index.month_name()
eques_wm.head()

## plot the earthquakes with basemap
ax = eques_wm.plot(figsize=(24,10), column='Magnitude(Local)', legend=True)
cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)
ax.set_axis_off()

# mask will be used to clip the GeoDataFrame to the area of interest
mask = gpd.GeoSeries.from_file('Data/mask.geojson')
mask_wm = mask.to_crs(epsg=3857)

# clip the data to the mask extend
eques_wm_clip = gpd.clip(eques_wm, mask_wm)
eques_wm_clip.head()
eques_wm_clip.shape

# download a CartoDB basemap based on mask boundaries
w, s, e, n = mask_wm.total_bounds

# using the above coordinates download the basemap in tif format 
_ = cx.bounds2raster(w, s, e, n,
                    ll=False,
                    zoom=12,
                    path='Data/heraklion_positron.tif',
                    source=cx.providers.CartoDB.Positron
                    )

ax = eques_wm_clip.plot(figsize=(24,10), column = 'Magnitude(Local)', legend=True)
cx.add_basemap(ax, source = 'Data/heraklion_positron.tif')
ax.set_axis_off()
plt.show()