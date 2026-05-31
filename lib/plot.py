import os
# from sklearn.cluster._hdbscan.hdbscan import labelling_at_cut
import contextily as cx # pyright: ignore[reportMissingImports]
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def make_colormap(n_colors):
    colors = (
        plt.cm.tab20.colors +
        plt.cm.tab20b.colors +
        plt.cm.tab20c.colors
    )  # 60 distinct colours total
    return mcolors.ListedColormap(colors[:n_colors])

def generate_basemap_path(w, s, e, n, z):
    return os.getcwd() + f"/basemaps/basemap_{w}_{s}_{e}_{n}_z{z}.tif"


# # download a CartoDB basemap based on bbox
def get_basemap(w=-180, s=-90, e=180, n=90, zoom=3):
    basemap_path = generate_basemap_path(w, s, e, n, zoom)
    if not os.path.exists(basemap_path):
        _ = cx.bounds2raster(w, s, e, n,
            ll=True, # set to True to use lat/lon coordinates
            zoom=zoom,  # zoom level 3 covers the entire world
            # change to 6-8 for regional views
            path=basemap_path,
            source=cx.providers.CartoDB.Positron,
        )
        return basemap_path
    else:
        return basemap_path


def hexbin_plot(gdf, gridsize=50, colormap="viridis",
                bbox: tuple | None = None, title=None, zoom=3):
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
    cx.add_basemap(ax,
        crs=gdf_copy.crs,
        source=basemap,
    )
    if title:
        ax.set_title(title)
    ax.set_axis_off()
    plt.show()


def cluster_plot(gdf, cluster_col="cluster_id", colormap="tab20", 
    bbox: tuple | None = None, title=None, zoom=3):

    # gdf_copy = gdf.copy()
    if bbox is not None:
        gdf = gdf.clip(bbox)
        basemap = get_basemap(*bbox, zoom=zoom)
    else:
        basemap = get_basemap(zoom=zoom)
    
    n_clusters = gdf[cluster_col].nunique() - 1  # exclude -1 noise
    cmap = make_colormap(n_clusters)

    fig, ax = plt.subplots(figsize=(24, 10))
    
    noise = gdf[gdf[cluster_col] == -1]
    noise.plot(
        ax=ax,
        color="black",
        markersize=0.5,
        label="Noise",
        legend=True,
    )
    
    clusters = gdf[gdf[cluster_col] != -1]
    clusters.plot(
        ax=ax,
        cmap=cmap,
        markersize=0.7,
        label="Clusters",
        legend=True,
        legend_kwds={"loc": "left"}
    )
    ax.set_xlim(gdf.bounds["minx"].min(), gdf.bounds["maxx"].max())
    ax.set_ylim(gdf.bounds["miny"].min(), gdf.bounds["maxy"].max())
    
    cx.add_basemap(ax,
        crs=gdf.crs,
        source=basemap,
    )
    ax.set_axis_off()
    plt.show()