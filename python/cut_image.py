import os
from PIL import Image
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import xml.etree.ElementTree as ET
from math import *

def cut_image_and_save(image_path, tile_size=32, num_tiles=64):
    def generate_tileset(image, tile_size, num_tiles):
        # Convertir l'image en tableau numpy
        image_array = np.array(image)

        # Diviser l'image en tuiles de la taille spécifiée
        tiles = []
        for y in range(0, image_array.shape[0], tile_size):
            for x in range(0, image_array.shape[1], tile_size):
                tile = image_array[y:y+tile_size, x:x+tile_size]
                tiles.append(tile)

        # Utiliser l'algorithme de clustering pour sélectionner les tuiles les plus représentatives
        kmeans = MiniBatchKMeans(n_clusters=num_tiles)
        kmeans.fit(np.array(tiles).reshape(-1, tile_size * tile_size * 3))
        centroids = kmeans.cluster_centers_.astype(int)

        # Créer l'image du tileset
        tileset_image = Image.new('RGB', (tile_size * int(np.sqrt(num_tiles)), tile_size * int(np.sqrt(num_tiles))))
        for i, centroid in enumerate(centroids):
            tile_image = Image.fromarray(centroid.reshape(tile_size, tile_size, 3).astype(np.uint8))
            tileset_image.paste(tile_image, (tile_size * (i % int(np.sqrt(num_tiles))), tile_size * (i // int(np.sqrt(num_tiles)))))

        return tileset_image, centroids

    def reconstruct_image(image, tileset, tile_size):
        width, height = image.size
        reconstructed_image = Image.new('RGB', (width, height))
        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):
                block = image.crop((x, y, x + tile_size, y + tile_size))
                block_data = np.array(block).reshape(-1, 3)
                min_dist = float('inf')
                closest_tile = None
                for tile in tileset:
                    tile_data = tile.reshape(-1, 3)
                    dist = np.sum((block_data - tile_data) ** 2)
                    if dist < min_dist:
                        min_dist = dist
                        closest_tile = tile
                closest_tile_image = Image.fromarray(closest_tile.reshape(tile_size, tile_size, 3).astype(np.uint8))
                reconstructed_image.paste(closest_tile_image, (x, y))
        return reconstructed_image

    def generate_tsx(tile_set_path): 
        root = ET.Element('tileset')
        root.set('name', f"tsx_{os.path.basename(image_path)}")
        root.set('tilewidth', str(tile_size))
        root.set('tileheight', str(tile_size))
        root.set('tilecount', str(num_tiles))
        root.set('columns', str(int(sqrt(num_tiles))))

        image = ET.SubElement(root, 'image')
        image.set('source', tile_set_path)
        image.set('trans', 'ff01fe')
        image.set('width', str(tile_size * int(sqrt(num_tiles))))
        image.set('height', str(tile_size * int(sqrt(num_tiles))))

        terraintypes = ET.SubElement(root, 'terraintypes')
        terraintypes.text = '\n '

        terrain = ET.SubElement(terraintypes, 'terrain')
        terrain.set('name', 'terrain')
        terrain.set('tile', '0')

        for i in range(num_tiles):
            tile = ET.SubElement(root, 'tile')
            tile.set('id', str(i))
            tile.tail = '\n '

        tree = ET.ElementTree(root)
        return tree



    # Chargement de l'image
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Génération du tileset
    tileset_image, tileset = generate_tileset(image, tile_size, num_tiles)

    # Sauvegarde du tileset
    folder_name = "tilesets"
    os.makedirs(folder_name, exist_ok=True)
    tileset_name = f"tileset_{os.path.basename(image_path)}"
    tileset_path = os.path.join(folder_name, tileset_name)
    tileset_image.save(tileset_path, format="PNG")

    # Reconstruction de l'image à partir du tileset
    reconstructed_image = reconstruct_image(image, tileset, tile_size)

    # Sauvegarde de l'image reconstruite
    reconstructed_image_name = f"reconstructed_{os.path.basename(image_path)}"
    reconstructed_image_path = os.path.join(folder_name, reconstructed_image_name)
    reconstructed_image.save(reconstructed_image_path, format="PNG")

    # Génération et sauvegarde du fichier TSX & TMX
    tsx_file = generate_tsx(tileset_path)
    folder_name = "tiled_file"
    os.makedirs(folder_name, exist_ok=True)
    path = os.path.splitext(os.path.basename(image_path))[0]
    tsx_name = f"tsx_{path}.tsx"
    tsx_path = os.path.join(folder_name, tsx_name)
    with open(tsx_path, 'wb') as f:
        tsx_file.write(f, encoding='utf-8', xml_declaration=True)



