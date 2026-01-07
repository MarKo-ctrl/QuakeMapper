from lib import get_data
from lib import transform
# from lib import plot
import subprocess

years = [2021, 2022]
get_data.get_earthquakes(years)

# from text lines to pandas (Geo)DataFrame...
eques_gdf_2021 = transform.text2df('Data/CAT2021.TXT', "EPSG:4326")
eques_gdf_2022 = transform.text2df('Data/CAT2022.TXT', "EPSG:4326")

transform.gdf_info(eques_gdf_2021)
transform.gdf_info(eques_gdf_2022)

# combine earthquakes data frames
eques_gdf = transform.combine_df([eques_gdf_2021, eques_gdf_2022])

# reproject to Web Mercator
eques_wm = transform.reproject(eques_gdf, 3857)
transform.gdf_info(eques_wm)

# mask will be used to clip the GeoDataFrame to the area of interest
mask_wm, eques_wm_clip = transform.clip_gdf(eques_wm, 'Data/mask.geojson', 3857)

# plot.quick_plot(eques_wm_clip, 'Data/heraklion_positron.tif')

transform.export2geojson(eques_wm_clip, 'Data/earthquakes.geojson')

# R plot
subprocess.run(['Rscript', r'.\earthquakes_plot.R', r'D:\python\QuakeMapper\Data\earthquakes.geojson'])