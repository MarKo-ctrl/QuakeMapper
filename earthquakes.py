from lib import get_data
from lib import transform
from lib.plot import monthly_frames, build_gif
from lib import plot
import contextily as ctx
import seaborn as sns
import numpy as np
# import subprocess
from pointpats import centrography
from matplotlib.patches import Ellipse


years = [2021, 2022]
get_data.get_earthquakes(years)

# from text lines to pandas (Geo)DataFrame...
eques_gdf_2021 = transform.text2df("Data/CAT2021.TXT", "EPSG:4326")
eques_gdf_2022 = transform.text2df("Data/CAT2022.TXT", "EPSG:4326")

transform.gdf_info(eques_gdf_2021)
transform.gdf_info(eques_gdf_2022)

# combine earthquakes data frames
eques_gdf = transform.combine_df([eques_gdf_2021, eques_gdf_2022])

# # reproject to Web Mercator
# eques_wm = transform.reproject(eques_gdf, 3857)
# transform.gdf_info(eques_wm)

# mask will be used to clip the GeoDataFrame to the area of interest
mask, eques_clip = transform.clip_gdf(eques_gdf,
                                            "Data/mask.geojson",
                                            4326)

# plot.quick_plot(eques_wm_clip, 'Data/heraklion_positron.tif')
plot.folium_plot(eques_clip,
                html_path='Data/earthquakes_map.html',
                zoom_start=8,
                tiles='CartoDB Positron')

# transform.export2geojson(eques_wm_clip, "Data/earthquakes.geojson")

# R plot
# Windows
# subprocess.run(['Rscript',
#             r'.\earthquakes_plot.R',
#             r'D:\python\QuakeMapper\Data\earthquakes.geojson'])
# Linux
# subprocess.run(["Rscript",
#                 r"earthquakes_plot.R",
#                 r"Data/earthquakes.geojson",
#                 "4"])

frames = monthly_frames(
    eques_clip,
    basemap_path='Data/heraklion_positron.tif',
    out_dir='frames',
    figsize=(10, 5))

build_gif(frames, 'frames/earthquakes.gif', seconds_per_frame=300)

print("Saved frames:", frames)

# add x and y columns for centrography
eques_clip["x"] = eques_clip["geometry"].x
eques_clip["y"] = eques_clip["geometry"].y

# calculate mean center and median center
mean_center = centrography.mean_center(eques_clip[["x", "y"]])
median_center = centrography.euclidean_median(eques_clip[["x", "y"]])

# calculate standard distance and ellipse parameters
cstd_dist = centrography.std_distance(eques_clip[["x", "y"]])
major, minor, rotation = centrography.ellipse(eques_clip[["x", "y"]])

# create joint plot with mean and median centers, and standard distance ellipse
joint_axes = sns.jointplot(
    data = eques_clip,
    x = eques_clip["x"],
    y = eques_clip["y"],
    s = 3,
    height = 7
)

joint_axes.ax_joint.scatter(
    *mean_center, color="red", marker="x", s=50, label="Mean Center"
)
joint_axes.ax_marg_x.axvline(mean_center[0],
                            color = "red")
joint_axes.ax_marg_y.axhline(mean_center[1],
                            color = "red")

joint_axes.ax_joint.scatter(
    *median_center, color="green", marker="o", s=50, label="Median Center"
)
joint_axes.ax_marg_x.axvline(median_center[0],
                            color = "limegreen")
joint_axes.ax_marg_y.axhline(median_center[1],
                            color = "limegreen")

ellipse = Ellipse(
    xy=mean_center,
    width=major * 2,
    height=minor * 2,
    angle=np.rad2deg(
        rotation
    ),
    facecolor="none",
    edgecolor="purple",
    linestyle="-.",
    label="Std. Ellipse",
)
joint_axes.ax_joint.add_patch(ellipse)

joint_axes.ax_joint.set_axis_off()
    
ctx.add_basemap(joint_axes.ax_joint,
                crs="EPSG:4326",
                source=ctx.providers.CartoDB.Positron
)

joint_axes.ax_joint.legend()
joint_axes.savefig("Data/centrography_plot.png", dpi=300)