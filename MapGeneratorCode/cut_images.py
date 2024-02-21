import os
from PIL import Image
import random
import Clustering


def cut_image_and_save(image_path):
    image = Image.open(image_path)

    width, height = image.size


    if width / height == 256 / 256:
        block_size = 8  # Réduisez la taille du bloc pour créer plus de tuiles
        tileset_images = []


        for y in range(0, height, block_size):
            for x in range(0, width, block_size):
                block = image.crop((x, y, x + block_size, y + block_size))
                tileset_images.append(block)


        if len(tileset_images) < 256:
            print("Pas assez d'images disponibles pour créer un tileset de 256 tuiles.")
            return



        selected_images = Clustering.cut_image_and_save(image_path)

        tileset_width = 16
        tileset = Image.new('RGB', (256, 256))



        for idx, tile_image in enumerate(selected_images):
            row = idx // tileset_width
            col = idx % tileset_width
            tile_image = tile_image.resize((16, 16))  # Redimensionnez chaque tuile à 16x16 pixels
            tileset.paste(tile_image, (col * 16, row * 16))



        folder_name = "tilesets"
        os.makedirs(folder_name, exist_ok=True)



        tileset_name = f"tileset_{os.path.basename(image_path)}"
        tileset_path = os.path.join(folder_name, tileset_name)
        tileset.save(tileset_path, format="PNG")

    else:
        print("L'image n'a pas le bon ratio.")



image_path = "Cabin_in_the_Woods.png"
cut_image_and_save(image_path)

