import numpy as np
from sklearn.cluster import KMeans


def kmeans_clustering(tileset_images,num_clusters):
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(tileset_images)
        cluster_centers = kmeans.cluster_centers_.astype(int)

        # Create tileset by selecting one image per cluster
        selected_images = []
        selected_clusters = set()
        for idx, center in enumerate(cluster_centers):
            closest_image_idx = np.argmin(np.linalg.norm(tileset_images - center, axis=1))
            if closest_image_idx not in selected_clusters:
                selected_images.append(tileset_images[closest_image_idx])
                selected_clusters.add(closest_image_idx)

        return selected_images
