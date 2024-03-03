import xml.etree.ElementTree as ET

def create_tsx_file(tsx_file_path, sourceFile, width, height, terrain_names, terrain_tiles, tileCount):
    # Crée l'élément racine 'tileset'
    root = ET.Element('tileset')
    root.set('name', 'Rooftops')
    root.set('tilewidth', '16')
    root.set('tileheight', '16')
    root.set('tilecount', tileCount)
    root.set('columns', '16')

    # Ajoute l'élément 'image' avec ses attributs
    image = ET.SubElement(root, 'image')
    image.set('source', sourceFile)
    image.set('trans', 'ff01fe')
    image.set('width', width)
    image.set('height', height)

    # Ajoute l'élément 'terraintypes' avec ses sous-éléments 'terrain'
    terraintypes = ET.SubElement(root, 'terraintypes')
    terraintypes.text = '\n  '


    for name, tile in zip(terrain_names, terrain_tiles):
        terrain = ET.SubElement(terraintypes, 'terrain')
        terrain.set('name', name)
        terrain.set('tile', str(tile))
        terrain.tail = '\n  '

    # Ajoute les éléments 'tile' avec leurs attributs
    for i in range(256):
        tile = ET.SubElement(root, 'tile')
        tile.set('id', str(i))
        tile.tail = '\n  '

        # Génère la chaîne de terrains pour chaque tile
        terrain_string = ''
        for j in range(4):
            if j < len(terrain_names):
                terrain_string += str(j) if terrain_tiles[j] == i else ','
            else:
                terrain_string += ','
        tile.set('terrain', terrain_string)

    # Crée l'objet ElementTree et écrit le fichier XML
    tree = ET.ElementTree(root)
    tree.write(tsx_file_path, encoding='utf-8', xml_declaration=True)

# Chemin du fichier TSX à créer
tsx_file_path = 'example.tsx'

# Définition des données pour la création du fichier TSX
sourceFile = 'Images/Set_F_Rooftops.png'
width = '256'
height = '256'
terrain_names = ["Roof1", "Roof2", "Roof3", "Roof4", "Roof5", "Roof6", "Roof7"]
terrain_tiles = [0, 5, 8, 13, 128, 133, 136]
tileCount = '256'

# Appelle la fonction pour créer le fichier TSX avec les nouvelles données
create_tsx_file(tsx_file_path, sourceFile, width, height, terrain_names, terrain_tiles, tileCount)

