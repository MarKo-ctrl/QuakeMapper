import os

import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def make_colormap():
    custom_colors = [
        "#42f8f8",
        "#a6cee3",
        "#1f78b4",
        "#b2df8a",
        "#33a02c",
        "#fb9a99",
        "#e31a1c",
        "#fdbf6f",
        "#ff7f00",
        "#cab2d6",
        "#6a3d9a",
        "#ffff99",
        "#b15928",
    ]
    return ListedColormap(custom_colors)


def generate_basemap_path(w, s, e, n, z):
    return os.getcwd() + f"/basemaps/basemap_{w}_{s}_{e}_{n}_z{z}.tif"


# download a basemap based on bbox
def get_basemap(w=-180, s=-90, e=180, n=90, zoom=3):
    basemap_path = generate_basemap_path(w, s, e, n, zoom)
    if not os.path.exists(basemap_path):
        _ = cx.bounds2raster(w, s, e, n,
            ll=True,  # set to True to use lat/lon coordinates
            zoom=zoom,  # zoom level 3 covers the entire world
            # change to 6-8 for regional views
            path=basemap_path,
            source=cx.providers.CartoDB.DarkMatterNoLabels,
        )
        return basemap_path
    else:
        return basemap_path


def hexbin_plot(
    gdf, gridsize=50, colormap="viridis", bbox: tuple | None = None, title=None, zoom=3
):
    gdf_copy = gdf.copy()
    if bbox is not None:
        gdf_copy = gdf_copy.clip(bbox)
        basemap = get_basemap(*bbox, zoom=zoom)
    else:
        basemap = get_basemap(zoom=zoom)
    gdf_copy["X"] = gdf_copy["geom"].x
    gdf_copy["Y"] = gdf_copy["geom"].y
    ax = gdf_copy.plot(
        kind="hexbin",
        x="X",
        y="Y",
        gridsize=gridsize,
        cmap=colormap,
        figsize=(24, 10),
        mincnt=1,
    )
    cx.add_basemap(
        ax,
        crs=gdf_copy.crs,
        source=basemap,
    )
    if title:
        ax.set_title(title)
    ax.set_axis_off()
    plt.show()


def get_plate_boundaries(filepath="data/PB2002_boundaries.json",
                         crs: int = 3857) -> gpd.GeoDataFrame:
    plate_boundaries = gpd.read_file(filepath)
    return plate_boundaries.to_crs(crs)


def cluster_plot(
    gdf, cluster_col="cluster_id", bbox: tuple | None = None, title=None, zoom=3
):
    plate_boundaries = get_plate_boundaries(crs=3857)
    colormap = make_colormap()

    if bbox is not None:
        gdf = gdf.clip(bbox)
        basemap = get_basemap(*bbox, zoom=zoom)
    else:
        basemap = get_basemap(zoom=zoom)

    clusters = gdf.to_crs(3857)
    base = clusters.plot(
        figsize=(24, 12),
        column=cluster_col,
        cmap=colormap,
        legend=True,
        categorical=True,
        markersize=0.7,
    )

    legend = base.get_legend()
    new_labels = [
        "Noise",
        "Cluster 1",
        "Cluster 2",
        "Cluster 3",
        "Cluster 4",
        "Cluster 5",
        "Cluster 6",
        "Cluster 7",
        "Cluster 8",
        "Cluster 9",
        "Cluster 10",
        "Cluster 11",
        "Cluster 12",
    ]
    for text, label in zip(legend.get_texts(), new_labels):
        text.set_text(label)
        
    plate_boundaries.plot(ax=base, color="white", linewidth=1.25, linestyle="dashdot")

    cx.add_basemap(
        base,
        crs=clusters.crs,
        source=basemap,
    )

    base.set_ylim(ymin=-14000000, ymax=25500000)
    if title:
        base.set_title(title)
    base.set_axis_off()
    plt.show()
