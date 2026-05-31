import numpy as np
from sklearn import metrics
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt


def degrees_to_radians(gdf):
    lats = gdf["geom"].y
    lons = gdf["geom"].x
    coords = np.column_stack((lats, lons))
    coords_radians = np.radians(coords)
    return coords_radians


def k_dist_plot(coords_radians, k):
    nn = NearestNeighbors(n_neighbors=k,
        metric="haversine",
        algorithm="ball_tree")
    nn.fit(coords_radians)
    distances, _ = nn.kneighbors(coords_radians)
    kth_distances = np.sort(distances[:, -1])
    plt.plot(kth_distances)
    plt.minorticks_on()
    plt.grid(True, which="both", linestyle="--")
    plt.xlabel("Count")
    plt.ylabel("Distance")
    plt.show()


def dbscan_clustering(coords_radians, eps, min_samples):
    db = DBSCAN(eps=eps,
        min_samples=min_samples,
        metric="haversine",
        algorithm="ball_tree")
    db.fit(coords_radians)
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = (labels == -1).sum()
    print(f"Estimated number of clusters: {n_clusters_}" )
    print(f"Estimated number of noise points: {n_noise_}")
    return labels
    