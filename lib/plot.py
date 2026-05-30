import os
# from numba.core import base
# import rasterio
# import rasterio.plot
# import imageio.v3 as iio
import contextily as cx # pyright: ignore[reportMissingImports]
import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# import folium
# import branca.colormap as cm


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
        colormap=colormap,
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


# def folium_plot(
#     gdf, html_path="earthquakes_map.html", zoom_start=8, tiles="CartoDB Positron"
# ):
#     """
#     Create a Folium map from a GeoDataFrame and save to an HTML file.

#     - Expects columns: 'Magnitude(Local)' and 'Depth(km)' (case-sensitive).
#     - The GeoDataFrame will be reprojected to EPSG:4326 (latitude/longitude).
#     - Each earthquake is drawn as a CircleMarker sized by magnitude and colored by depth.
#     Returns the folium.Map object and saves HTML at `html_path`.
#     """
#     # ensure we work in WGS84 lat/lon
#     gdf_wgs = gdf.to_crs(epsg=4326)
#     # center map on mean coordinates
#     center = [gdf_wgs.geometry.y.mean(), gdf_wgs.geometry.x.mean()]
#     m = folium.Map(location=center, zoom_start=zoom_start, tiles=tiles)
#     # prepare colormap for depth
#     depth_col = "Depth(km)"
#     if depth_col in gdf_wgs.columns and not gdf_wgs[depth_col].isna().all():
#         min_depth = float(gdf_wgs[depth_col].min())
#         max_depth = float(gdf_wgs[depth_col].max())
#         colormap = cm.linear.Oranges_09.scale(min_depth, max_depth)
#         colormap.caption = "Depth (km)"
#         m.add_child(colormap)
#     else:
#         colormap = None

#     mag_col = "Magnitude(Local)"
#     for idx, row in gdf_wgs.iterrows():
#         lon = row.geometry.x
#         lat = row.geometry.y
#         mag = row.get(mag_col, None)
#         depth = row.get(depth_col, None)
#         # popup content
#         date = (
#             idx.strftime("%Y-%m-%d")
#             if hasattr(idx, "strftime")
#             else row.get("Date", "")
#         )
#         popup_html = f"Date: {date}<br>Mag: {mag}<br>Depth: {depth} km"
#         # radius scaling (fallbacks for missing mag)
#         try:
#             radius = max(2, 2 + float(mag) * 2) if mag is not None else 3
#         except Exception:
#             radius = 3
#         # color from colormap or default
#         color = (
#             colormap(depth)
#             if (colormap is not None and depth is not None)
#             else "#3388ff"
#         )
#         folium.CircleMarker(
#             location=[lat, lon],
#             radius=radius,
#             color=color,
#             fill=True,
#             fill_color=color,
#             fill_opacity=0.7,
#             popup=folium.Popup(popup_html, max_width=300),
#         ).add_to(m)

#     m.save(html_path)
#     return m


# def monthly_frames(gdf_plot,
#                 basemap_path = "Data/heraklion_positron.tif",
#                 out_dir = "frames",
#                 figsize = (14, 9),
#                 dpi = 300,
#                 cmap = "copper_r",
#                 size_scale = 5,
#                 title_suffix = None):
#     """
#     Create one PNG map per month and combine into a GIF.

#     - Expects GeoDataFrame `gdf` with geometry and columns:
#         'Magnitude(Local)' and 'Depth(km)'.
#     - Assumes or reprojects to EPSG:3857 (Web Mercator) to match basemap.
#     - Groups by month-name (January..December). Months with no events are skipped.
#     Returns list_of_frames, gif_path.
#     """
#     os.makedirs(out_dir, exist_ok=True)

#     # compute global padded bounds (do this once, before the monthly loop)
#     global_minx, global_miny, global_maxx, global_maxy = gdf_plot.total_bounds
#     pad = max(global_maxx - global_minx, global_maxy - global_miny) * 0.08  # 8% padding
#     xmin = global_minx - pad
#     xmax = global_maxx + pad
#     ymin = global_miny - pad
#     ymax = global_maxy + pad

#     # consistent depth scale across months
#     depth_col = "Depth(km)"
#     if depth_col in gdf_plot.columns and not gdf_plot[depth_col].isna().all():
#         vmin = float(gdf_plot[depth_col].min())
#         vmax = float(gdf_plot[depth_col].max())
#     else:
#         vmin, vmax = None, None

#     # add Year and Month columns for grouping
#     gdf_plot["Year"] = gdf_plot["Date"].dt.year
#     gdf_plot["Month"] = gdf_plot["Date"].dt.strftime("%B")
#     gdf_plot["YearMonth"] = gdf_plot["Date"].dt.to_period("M")

#     # read basemap once
#     with rasterio.open(basemap_path) as src:
#         basemap_img = src.read()  # shape (bands, rows, cols)

#         # basemap extent from raster: (left, right, bottom, top)
#         bm_left, bm_right, bm_bottom, bm_top = (
#             src.bounds.left,
#             src.bounds.right,
#             src.bounds.bottom,
#             src.bounds.top,)

#     # intersect with basemap to avoid showing area outside raster; fallback to padded bounds
#     final_xmin = max(xmin, bm_left)
#     final_xmax = min(xmax, bm_right)
#     final_ymin = max(ymin, bm_bottom)
#     final_ymax = min(ymax, bm_top)

#     # if intersection is empty (unlikely), just use padded bounds
#     if final_xmin >= final_xmax or final_ymin >= final_ymax:
#         final_xmin, final_xmax, final_ymin, final_ymax = xmin, xmax, ymin, ymax

#     frames = []

#     # Get unique Year-Month combinations sorted chronologically
#     year_months = sorted(gdf_plot["YearMonth"].unique())

#     idx = 1
#     for ym in year_months:
#         sub = gdf_plot[gdf_plot["YearMonth"] == ym]
#         if sub.empty:
#             continue

#         fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
#         fig.subplots_adjust(left=0.05, right=0.9, top=0.95, bottom=0.05)

#         # plot basemap
#         # rasterio.read returns (bands, rows, cols) --> transpose for imshow: (rows, cols, bands)
#         img = np.transpose(basemap_img, (1, 2, 0))
#         ax.imshow(img, extent=(bm_left, bm_right, bm_bottom, bm_top), origin="upper")
#         # determine plotting window to zoom to subset bounds with small padding
#         minx, miny, maxx, maxy = sub.total_bounds
#         ax.set_xlim(final_xmin, final_xmax)
#         ax.set_ylim(final_ymin, final_ymax)

#         # scatter: size by magnitude, color by depth
#         mags = sub.get("Magnitude(Local)")
#         depths = sub.get(depth_col) if depth_col in sub.columns else None
#         sizes = (mags.fillna(mags.mean()) ** 2) * size_scale

#         ax.scatter(
#             sub.geometry.x,
#             sub.geometry.y,
#             s=sizes,
#             c=depths if depths is not None else "red",
#             cmap=cmap if (vmin is not None) else None,
#             vmin=vmin,
#             vmax=vmax,
#             alpha=0.75,
#             edgecolor="k",
#             linewidth=0.2,
#             zorder=10,)

#         if vmin is not None and vmax is not None:
#             import matplotlib as mpl

#             norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
#             sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
#             sm._A = []
#             cax = fig.add_axes([0.92, 0.2, 0.02, 0.6])  # fixed position for all frames
#             fig.colorbar(sm, cax=cax, label="Depth (km)")

#         # title with year and month
#         month_name = ym.strftime("%B")
#         year = ym.year
#         ax.set_title(f"Earthquakes in {month_name} {year}")
#         ax.set_axis_off()

#         fname = os.path.join(out_dir, f"frame_{idx:02d}_{year}_{month_name}.png")
#         fig.savefig(fname, dpi=dpi)
#         plt.close(fig)
#         frames.append(fname)
#         idx += 1

#     if not frames:
#         raise RuntimeError(
#             "No monthly frames produced (input GeoDataFrame may be empty)."
#         )
#     return frames

# def build_gif(frames, gif_path, seconds_per_frame):
# imgs = [iio.imread(f) for f in frames]
# iio.imwrite(gif_path, imgs, duration=seconds_per_frame)
