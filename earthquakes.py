from lib import clustering, db_queries, plot

# get_data.fetch_all(2000, 2003)
# get_data.fetch_all(2003, 2005)
# get_data.fetch_all(2005, 2010)
# get_data.fetch_all(2010, 2026)

# eq_2010 = db_queries.load_by_year_range(2010, 2010)

# plot.hexbin_plot(eq_2010,
#     bbox=(-141.85,-40.97,-3.51,60.41),
#     title="2010 Earthquakes in America",
#     gridsize=100,
#     zoom=5)

# eq_2011 = db_queries.load_by_year_range(2011, 2011)

# coords_radians = clustering.degrees_to_radians(eq_2011)
# clustering.k_dist_plot(coords_radians, k=500)

all_eq = db_queries.load_all()
coords_radians = clustering.degrees_to_radians(all_eq)
# clustering.k_dist_plot(coords_radians, k=200)
labels = clustering.dbscan_clustering(coords_radians, eps=0.06, min_samples=1500)
all_eq["cluster_id"] = labels
print(all_eq.groupby("cluster_id").size().sort_values(ascending=False))
# all_eq.to_csv("all_eq.csv", index=False)
# plot.cluster_plot(all_eq, title="Earthquakes Clusters")

# plot.hexbin_plot(eq_2011,
#     bbox=(-180,-66.50,180,84),
#     title="2011 Earthquakes - World",
#     gridsize=200,
#     zoom=4)

# eq_45_5 = db_queries.load_magnitude_range(4.5, 5.1)
# print(eq_45_5.head(10))

# cal_eq = db_queries.load_by_bbox(*(-125.222168,30.845647,-113.884277,39.487085))
# print(cal_eq.shape)
