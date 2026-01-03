import matplotlib.pyplot as plt
import contextily as cx
import os

# # download a CartoDB basemap based on mask boundaries
def get_basemap(extend_obj, basemap_path):
    if not os.path.exists(basemap_path):
        w, s, e, n = extend_obj.total_bounds
        # using the above coordinates download the basemap in tif format
        _ = cx.bounds2raster(w, s, e, n,
                            ll = False,
                            zoom = 12,
                            path = basemap_path,
                            source = cx.providers.CartoDB.Positron)
        return basemap_path
    else:
        return basemap_path


def quick_plot(gdf, basemap_path):
    ax = gdf.plot(figsize=(24,10), column = 'Magnitude(Local)', legend=True)
    cx.add_basemap(ax, source = get_basemap(gdf, basemap_path))
    ax.set_axis_off()
    plt.show()



