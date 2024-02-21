import os
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans


def cut_image_and_save(image_path):
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")  # Convertir en mode RGB si ce n'est pas déjà le cas

    width, height = image.size
    if width / height == 256 / 256:
        block_size = 16
        tileset_images = []
        for y in range(0, height, block_size):
            for x in range(0, width, block_size):
                block = image.crop((x, y, x + block_size, y + block_size))
                tileset_images.append(np.array(block).flatten())

        # Perform K-means clustering
        num_clusters = 128
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

        # Create tileset image
        tileset_width = 8
        tileset_height = 8
        tileset = Image.new('RGB', (128, 256))
        for idx, tile_data in enumerate(selected_images):
            tile_image = Image.fromarray(tile_data.reshape((block_size, block_size, 3)))
            row = idx // tileset_width
            col = idx % tileset_width
            tileset.paste(tile_image, (col * block_size, row * block_size))

        folder_name = "tilesets"
        os.makedirs(folder_name, exist_ok=True)
        tileset_name = f"tileset_{os.path.basename(image_path)}"
        tileset_path = os.path.join(folder_name, tileset_name)
        tileset.save(tileset_path, format="PNG")
    else:
        print("L'image n'a pas le ratio 256:256.")
    
    return selected_images

