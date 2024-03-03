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
        tile_ids = []  # Pour stocker les IDs correspondants à chaque tuile
        for i, y in enumerate(range(0, image_array.shape[0], tile_size)):
            for x in range(0, image_array.shape[1], tile_size):
                tile = image_array[y:y+tile_size, x:x+tile_size]
                tiles.append(tile)

        # Utiliser l'algorithme de clustering pour sélectionner les tuiles les plus représentatives
        kmeans = MiniBatchKMeans(n_clusters=num_tiles)
        kmeans.fit(np.array(tiles).reshape(-1, tile_size * tile_size * 3))
        centroids = kmeans.cluster_centers_.astype(int)

        # Créer l'image du tileset avec les IDs correspondants
        tileset_image = Image.new('RGB', (tile_size * int(np.sqrt(num_tiles)), tile_size * int(np.sqrt(num_tiles))))
        for i, centroid in enumerate(centroids):
            tile_image = Image.fromarray(centroid.reshape(tile_size, tile_size, 3).astype(np.uint8))
            tileset_image.paste(tile_image, (tile_size * (i % int(np.sqrt(num_tiles))), tile_size * (i // int(np.sqrt(num_tiles)))))
            tile_ids.append(i)  # Assigner un ID unique à chaque tuile

        return tileset_image, centroids, tile_ids

    def reconstruct_image(image, tileset, tile_size, tile_ids):
        width, height = image.size
        reconstructed_image = Image.new('RGB', (width, height))
        used_tile_ids = []  # Pour stocker les IDs des tuiles utilisées
        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):
                block = image.crop((x, y, x + tile_size, y + tile_size))
                block_data = np.array(block).reshape(-1, 3)
                min_dist = float('inf')
                closest_tile = None
                closest_tile_id = None
                for i, tile in enumerate(tileset):
                    tile_data = tile.reshape(-1, 3)
                    dist = np.sum((block_data - tile_data) ** 2)
                    if dist < min_dist:
                        min_dist = dist
                        closest_tile = tile
                        closest_tile_id = tile_ids[i]  # Récupérer l'ID correspondant à la tuile
                closest_tile_image = Image.fromarray(closest_tile.reshape(tile_size, tile_size, 3).astype(np.uint8))
                reconstructed_image.paste(closest_tile_image, (x, y))
                used_tile_ids.append(closest_tile_id)  # Enregistrer l'ID de la tuile utilisée
        return reconstructed_image, used_tile_ids

    def generate_tsx(tileset_path, tile_ids): 
        root = ET.Element('tileset')
        root.set('name', f"tsx_{os.path.basename(image_path)}")
        root.set('tilewidth', str(tile_size))
        root.set('tileheight', str(tile_size))
        root.set('tilecount', str(len(tile_ids)))  # Utiliser le nombre total de tuiles
        root.set('columns', str(int(sqrt(len(tile_ids)))))

        image = ET.SubElement(root, 'image')
        image.set('source', tileset_path)
        image.set('trans', 'ff01fe')
        image.set('width', str(tile_size * int(sqrt(len(tile_ids)))))
        image.set('height', str(tile_size * int(sqrt(len(tile_ids)))))

        terraintypes = ET.SubElement(root, 'terraintypes')
        terraintypes.text = '\n '

        terrain = ET.SubElement(terraintypes, 'terrain')
        terrain.set('name', 'terrain')
        terrain.set('tile', '0')

        # Utiliser les IDs des tuiles pour créer les éléments <tile>
        for i, tile_id in enumerate(tile_ids):
            tile = ET.SubElement(root, 'tile')
            tile.set('id', str(i))
            tile.tail = '\n '

        tree = ET.ElementTree(root)
        return tree

    def generate_tmx(tsx_path, used_tile_ids):
        root = ET.Element('map')
        root.set('version', '1.0')
        root.set('orientation', 'orthogonal')
        root.set('renderorder', 'right-down')
        root.set('width', '16')
        root.set('height', '16')
        root.set('tilewidth', str(tile_size))
        root.set('tileheight', str(tile_size))
        root.set('nextobjectid', '1')
        root.text = '\n '

        tileset = ET.SubElement(root, 'tileset')
        tileset.set('firstgid', '1')
        tileset.set('source', tsx_path)
        tileset.tail = '\n '

        layer = ET.SubElement(root, 'layer')
        layer.set('name', 'Tile Layer 6')
        layer.set('width', '16')
        layer.set('height', '16')
        layer.tail = '\n '
        layer.text = '\n '  

        data = ET.SubElement(layer, 'data')
        data.set('encoding', 'csv')

        # Utiliser les IDs des tuiles utilisées pour remplir les données
        data.text = ','.join(str(tile_id) for tile_id in used_tile_ids)
        data.tail = '\n '

        tree = ET.ElementTree(root)
        return tree

    # Chargement de l'image
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Génération du tileset
    tileset_image, tileset, tile_ids = generate_tileset(image, tile_size, num_tiles)

    # Sauvegarde du tileset
    folder_name = "tilesets"
    os.makedirs(folder_name, exist_ok=True)
    tileset_name = f"tileset_{os.path.basename(image_path)}"
    tileset_path = os.path.join(folder_name, tileset_name)
    tileset_image.save(tileset_path, format="PNG")

    # Reconstruction de l'image à partir du tileset
    reconstructed_image, used_tile_ids = reconstruct_image(image, tileset, tile_size, tile_ids)
    
    # Sauvegarde de l'image reconstruite
    reconstructed_image_name = f"reconstructed_{os.path.basename(image_path)}"
    reconstructed_image_path = os.path.join(folder_name, reconstructed_image_name)
    reconstructed_image.save(reconstructed_image_path, format="PNG")

    # Génération et sauvegarde du fichier TSX & TMX
    tsx_file = generate_tsx(tileset_path, tile_ids)
    folder_name = "tiled_file"
    os.makedirs(folder_name, exist_ok=True)
    path = os.path.splitext(os.path.basename(image_path))[0]
    tsx_name = f"tsx_{path}.tsx"
    tsx_path = os.path.join(folder_name, tsx_name)
    tsx_file.write(tsx_path, encoding='utf-8', xml_declaration=True)

    tmx_file = generate_tmx(tsx_path, used_tile_ids)
    tmx_name = f"tmx_{path}.tmx"
    tmx_path = os.path.join(folder_name, tmx_name)
    tmx_file.write(tmx_path, encoding='utf-8', xml_declaration=True)
