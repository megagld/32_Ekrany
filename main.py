from pyzwcad import ZwCAD, APoint
import os
import json
from classes import *
from drawer import *


ekran = AcousticScreen()

# tworzenie profilu terenu
input_dir = os.getcwd()
project_data_dir = '{}\\{}'.format(input_dir, '_project')
terrain_data_path = '{}\\{}\\{}'.format(input_dir, '_project', '01_Terrain_data')

# pobiera pliki z katalogu _data i podkatalogów
    
for root, _, files in os.walk(terrain_data_path):
    for file in files:
        if file.endswith('.json'):
            terrain_path = os.path.join(terrain_data_path, file)

            with open(terrain_path, "r") as f:
                data = json.load(f)
            
            ekran.terrain_profile = Terrain()
            ekran.terrain_profile.description_name = file[:-13]
            ekran.terrain_profile.profile = data


# tworzy obiekt "malarza" i rysuje profil terenu

drawer = Drawer()

drawer.draw_terrain(ekran.terrain_profile)



