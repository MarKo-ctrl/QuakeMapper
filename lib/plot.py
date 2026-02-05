import matplotlib.pyplot as plt
import contextily as cx
import os
import folium
import branca.colormap as cm


# # download a CartoDB basemap based on mask boundaries
def get_basemap(extend_obj, basemap_path):
    if not os.path.exists(basemap_path):
        w, s, e, n = extend_obj.total_bounds
        # using the above coordinates download the basemap in tif format
        _ = cx.bounds2raster(
            w,
            s,
            e,
            n,
            ll=False,
            zoom=12,
            path=basemap_path,
            source=cx.providers.CartoDB.Positron,
        )
        return basemap_path
    else:
        return basemap_path


def quick_plot(gdf, basemap_path):
    ax = gdf.plot(figsize=(24, 10), column="Magnitude(Local)", legend=True)
    cx.add_basemap(ax, source=get_basemap(gdf, basemap_path))
    ax.set_axis_off()
    plt.show()


def folium_plot(
    gdf, html_path="earthquakes_map.html", zoom_start=8, tiles="CartoDB Positron"
):
    """
    Create a Folium map from a GeoDataFrame and save to an HTML file.

    - Expects columns: 'Magnitude(Local)' and 'Depth(km)' (case-sensitive).
    - The GeoDataFrame will be reprojected to EPSG:4326 (latitude/longitude).
    - Each earthquake is drawn as a CircleMarker sized by magnitude and colored by depth.
    Returns the folium.Map object and saves HTML at `html_path`.
    """
    # ensure we work in WGS84 lat/lon
    gdf_wgs = gdf.to_crs(epsg=4326)
    # center map on mean coordinates
    center = [gdf_wgs.geometry.y.mean(), gdf_wgs.geometry.x.mean()]
    m = folium.Map(location=center, zoom_start=zoom_start, tiles=tiles)
    # prepare colormap for depth
    depth_col = "Depth(km)"
    if depth_col in gdf_wgs.columns and not gdf_wgs[depth_col].isna().all():
        min_depth = float(gdf_wgs[depth_col].min())
        max_depth = float(gdf_wgs[depth_col].max())
        colormap = cm.linear.Oranges_09.scale(min_depth, max_depth)
        colormap.caption = "Depth (km)"
        m.add_child(colormap)
    else:
        colormap = None

    mag_col = "Magnitude(Local)"
    for idx, row in gdf_wgs.iterrows():
        lon = row.geometry.x
        lat = row.geometry.y
        mag = row.get(mag_col, None)
        depth = row.get(depth_col, None)
        # popup content
        date = (
            idx.strftime("%Y-%m-%d")
            if hasattr(idx, "strftime")
            else row.get("Date", "")
        )
        popup_html = f"Date: {date}<br>Mag: {mag}<br>Depth: {depth} km"
        # radius scaling (fallbacks for missing mag)
        try:
            radius = max(2, 2 + float(mag) * 2) if mag is not None else 3
        except Exception:
            radius = 3
        # color from colormap or default
        color = (
            colormap(depth)
            if (colormap is not None and depth is not None)
            else "#3388ff"
        )
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(m)

    m.save(html_path)
    return m
