import os
from PIL import Image
import numpy as np
from mkeans_clustering import kmeans_clustering


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

        selected_images = kmeans_clustering(tileset_images)

        # Create tileset image
        tileset_width = 16
        tileset_height = 8
        tileset = Image.new('RGB', (256, 256))
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

