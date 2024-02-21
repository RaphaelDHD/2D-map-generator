from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

def extract_tiles(image_path, tile_size):
    # Charger l'image de la carte 2D
    image = Image.open(image_path)
    width, height = image.size

    tiles = []

    # Parcourir l'image et extraire chaque tuile
    for y in range(0, height, tile_size[1]):
        for x in range(0, width, tile_size[0]):
            # Extraire la tuile à partir de l'image
            tile = image.crop((x, y, x + tile_size[0], y + tile_size[1]))
            tiles.append(tile)

    return tiles


def select_representative_tiles(tiles):
    # Convertir les tuiles en tableaux numpy
    tile_arrays = [np.array(tile) for tile in tiles]

    # Convertir les tableaux en un seul tableau 2D
    flat_tile_array = np.array(tile_arrays).reshape(len(tiles), -1)

    # Utiliser l'algorithme KMeans pour regrouper les tuiles
    kmeans = KMeans(n_clusters=256)
    kmeans.fit(flat_tile_array)

    # Sélectionner un représentant de chaque cluster
    representative_indices = []
    for cluster_center in kmeans.cluster_centers_:
        # Calculer les distances entre le centre du cluster et toutes les tuiles
        distances = np.linalg.norm(flat_tile_array - cluster_center, axis=1)

        # Trouver l'index de la tuile la plus proche du centre du cluster
        closest_tile_index = np.argmin(distances)

        # Ajouter l'index de la tuile sélectionnée à la liste des indices de tuiles représentatives
        representative_indices.append(closest_tile_index)

    # Sélectionner les tuiles représentatives en fonction des indices obtenus
    representative_tiles = [tiles[index] for index in representative_indices]

    return representative_tiles


def save_tiles(tiles, output_path):
    for i, tile in enumerate(tiles):
        try:
            tile.save(f"{output_path}/tile_{i}.png", "PNG")
        except Exception as e:
            print(f"Error saving tile {i}: {e}")

# Chemin de l'image de la carte 2D
image_path = "2024-02-20_15-15-05_7307.png"  # Remplacez par le chemin de votre image

# Taille des tuiles
tile_size = (32, 32)

# Extraire les tuiles
tiles = extract_tiles(image_path, tile_size)

# Sélectionner les 32 tuiles les plus pertinentes
representative_tiles = select_representative_tiles(tiles)

# Enregistrer chaque tuile représentative au format PNG
output_path = "output_folder"  # Remplacez par le chemin du dossier de sortie
save_tiles(representative_tiles, output_path)
