import matplotlib.pyplot as plt
from scipy import stats

from lib import db_queries, get_data
from lib.db_setup import add_table_column

# data layers for Q2
if db_queries.table_exists_complete("polygon_plate_boundaries"):
    print("Table exists in DB")
else:
    get_data.geojson_to_postgis("data/PB2002_plates.json", "polygon_plate_boundaries")
    add_table_column("earthquakes", "plate_name", "TEXT")

magnitude = db_queries.load_magnitude()

fig, (ax_hist, ax_qq) = plt.subplots(1, 2, figsize=(12, 5))

ax_hist.hist(magnitude, bins=30, edgecolor="black")
ax_hist.set_title("Histogram of Earthquake Magnitudes")
ax_hist.set_xlabel("Magnitude")
ax_hist.set_ylabel("Count")

stats.probplot(magnitude, dist="norm", plot=ax_qq)
ax_qq.set_title("Q-Q Plot of Earthquake Magnitudes")

fig.tight_layout()
fig.savefig("plots/magnitude_qq_plot.png")
plt.close(fig)


