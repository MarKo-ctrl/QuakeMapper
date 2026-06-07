from lib import clustering, db_queries, plot, db_setup, get_data

get_data.fetch_all(2000, 2003)
get_data.fetch_all(2003, 2005)
get_data.fetch_all(2005, 2010)
get_data.fetch_all(2010, 2026)

# events in 2010
eq_2010 = db_queries.load_by_year_range(2010, 2010)

# hexbin map of 2010 earthquakes
plot.hexbin_plot(eq_2010,
    bbox=(-141.85,-40.97,-3.51,60.41),
    title="2010 Earthquakes in America",
    gridsize=100,
    zoom=5)

# events in 2011
eq_2011 = db_queries.load_by_year_range(2011, 2011)

# hexbin map of 2011 earthquakes
plot.hexbin_plot(eq_2011,
    bbox=(-180,-66.50,180,84),
    title="2011 Earthquakes - World",
    gridsize=200,
    zoom=4)

# k-distance plot for 2011 earthquakes
coords_radians = clustering.degrees_to_radians(eq_2011)
clustering.k_dist_plot(coords_radians, k=500)

# cluster_id column will store the cluster labels
db_setup.add_table_column("earthquakes", "cluster_id", "INTEGER")

# fetch all earthquakes and cluster them
all_eq = db_queries.load_all()
coords_radians = clustering.degrees_to_radians(all_eq)
clustering.k_dist_plot(coords_radians, k=200)
labels = clustering.dbscan_clustering(coords_radians, eps=0.06, min_samples=1000)
all_eq["cluster_id"] = labels
print(all_eq.groupby("cluster_id").size().sort_values(ascending=False))  # pyright: ignore[reportCallIssue]

# update the cluster labels in the database
db_queries.update_cluster_labels(all_eq, "earthquakes", "cluster_id")
plot.cluster_plot(all_eq, title="Earthquakes Clusters", zoom=4)
