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
piles_data_path = '{}\\{}\\{}'.format(input_dir, '_project', '03_Piles_data')


# pobiera pliki z katalogu _data i podkatalogów
# profil terenu
    
for root, _, files in os.walk(terrain_data_path):
    for file in files:
        if file.endswith('.json'):
            terrain_path = os.path.join(terrain_data_path, file)

            with open(terrain_path, "r") as f:
                data = json.load(f)
            
            ekran.terrain_profile = Terrain()
            ekran.terrain_profile.description_name = f'terrain_{file[:-13]}'
            for number, point_data in enumerate(data, 1):
                ekran.terrain_profile.profile[number] = point_data

                # dodanie pozyzji Z=0 jeśli brakuje w danych
                ekran.terrain_profile.add_Z_values_to_terrain()

            # przeskalowanie na osi y
            ekran.terrain_profile.scale_Y_axis()
            

            f.close()

# wspórzędne pali

for root, _, files in os.walk(piles_data_path):
    for file in files:
        if file.endswith('.json'):
            piles_path = os.path.join(piles_data_path, file)

            with open(piles_path, "r") as f:
                data = json.load(f)
            
            for number, position in enumerate(data, 1):
                ekran.piles[number] = Pile()
                ekran.piles[number].description_name = f'pile_{file[:-10]}_{number:03d}'
                ekran.piles[number].position = position
                # dodanie pozyzji Z=0 jeśli brakuje w danych
                ekran.piles[number].add_Z_value()


            # xxxxxxxxxxxxxx USUŃ xxxxxxxxxxxxxxxxx
                ekran.piles[number].diameter = 0.6
            # xxxxxxxxxxxxxx USUŃ xxxxxxxxxxxxxxxxx

            f.close()

# tworzenie obiektów paneli na podstawie lokalizacji pali

for number, pile in enumerate(ekran.piles.values(),1):
    if number<len(ekran.piles):
        ekran.panels[number] = Panel()
        ekran.panels[number].number = number
        ekran.panels[number].description_name = pile.description_name.replace('pile', 'panel')
        ekran.panels[number].position = pile.position
        ekran.panels[number].end_position = ekran.piles[number+1].position
        ekran.panels[number].calc_width() 



# tworzy obiekt "malarza" i
drawer = Drawer()

# #  rysuje profil terenu
drawer.draw_terrain(ekran.terrain_profile)


# rysuje pale na planie
# drawer.draw_piles_on_plan(ekran.piles)


for i in ekran.panels.values():
    print(i.width)