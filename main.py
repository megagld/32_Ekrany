from pyzwcad import ZwCAD, APoint
import os
import json
from classes import *
from drawer import *
import math


ekran = AcousticScreen()


# pobiera pliki z katalogu _data i podkatalogów
input_dir = os.getcwd()
project_data_dir = '{}\\{}'.format(input_dir, '_project')
terrain_data_path = '{}\\{}'.format(project_data_dir, '01_Terrain_data')
piles_data_path = '{}\\{}'.format(project_data_dir, '03_Piles_data')
poles_data_path = '{}\\{}'.format(project_data_dir, '04_Poles_data')


# ustalenie przesunięcia pala wzgledem profilu rozwiniecia terenu
# oznacza w którym miejscu na profilu terenu jest pierwsza oś    

ekran.terain_milage_dalay = 0.01

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
                x_position_on_profile = point_data[0]
                z = point_data[1]
                ekran.terrain_profile.profile[number] = Point(z=z, 
                                                              x_position_on_profile = x_position_on_profile)

            # przeskalowanie na osi Z
            ekran.terrain_profile.scale_Z_axis()
            f.close()
            # przesunięcie terenu na profilu wzgledem pali
            ekran.terrain_profile.move_terrain_horizontaly(ekran.terain_milage_dalay)

# przesunięcie poziome terenu

ekran.terrain_profile.move_terrain_horizontaly(ekran.terain_milage_dalay)

# wspórzędne pali

for root, _, files in os.walk(piles_data_path):
    for file in files:
        if file.endswith('_coordinates.json'):
            piles_path = os.path.join(piles_data_path, file)

            with open(piles_path, "r") as f:
                data = json.load(f)
            
            for number, position in enumerate(data, 1):
                ekran.piles[number] = Pile()
                ekran.piles[number].description_name = f'pile_{file[:-10]}_{number:03d}'

                ekran.piles[number].x_coord = position[0]
                ekran.piles[number].y_coord = position[1]

                # dodanie pozyzji Z=0 jeśli brakuje w danych
                try:
                    ekran.piles[number].z_coord = position[2]
                except:
                    ekran.piles[number].z_coord = 0



            # xxxxxxxxxxxxxx USUŃ xxxxxxxxxxxxxxxxx
                ekran.piles[number].diameter = 0.6
            # xxxxxxxxxxxxxx USUŃ xxxxxxxxxxxxxxxxx

            f.close()

# ustalenie głównych osi przęseł

# tworzenie osi głównych na podstawie współrzędnych pali

for number, pile in enumerate(ekran.piles.values(),1):
    ekran.main_axes[number] = MainAxis()
    ekran.main_axes[number].number = number
    ekran.main_axes[number].description_name = pile.description_name.replace('pile', 'axis')
    ekran.main_axes[number].x_coord = pile.x_coord
    ekran.main_axes[number].y_coord = pile.y_coord

#  ustalenie odległości miedzy osiami

distance_on_profile = 0

for axis_number, axis in ekran.main_axes.items():
    axis.distance_on_profile = distance_on_profile
    if axis_number<len(ekran.main_axes):
        axis.calc_width(ekran.main_axes[axis_number+1])
        distance_on_profile += axis.next_span_length
        
# ustalenie długości ekranu na profilu
ekran.length = distance_on_profile

# Sprawdzenie czy osie nie są poza dostępnym profilem terenu
if any((ekran.terrain_profile.profile[1].x_position_on_profile > 0,
       ekran.terrain_profile.profile[max(ekran.terrain_profile.profile)].x_position_on_profile < ekran.length)):
    print('brakuje profilu terenu')

# oblicznie rzędnych terenu w osiach głównych

for axis_number, axis in ekran.main_axes.items():

    for number, terrain_point in ekran.terrain_profile.profile.items():

        if axis.distance_on_profile>terrain_point.x_position_on_profile:
            delta_x = ekran.terrain_profile.profile[number+1].x_position_on_profile - terrain_point.x_position_on_profile
            delta_y = ekran.terrain_profile.profile[number+1].z - terrain_point.z
            axis_delta_x = axis.distance_on_profile - terrain_point.x_position_on_profile
            axis.terrain_z_position = (axis_delta_x/delta_x)*delta_y + terrain_point.z
            ekran.terrain_profile.new_tarrain_profile[axis_number] = Point(x_position_on_profile = axis.distance_on_profile, 
                                                                           z = axis.terrain_z_position)


# obliczanie rzędnych pali na osiach głównych

for axis in ekran.main_axes.values():
    axis.z_coord_pile = math.ceil(10*(axis.terrain_z_position))/10 + ekran.min_elevation
    

# tworzenie obiektów słupów i ustalenie ich wysokości

# na razie analogicznie do starego skryptu - tj. ręcznie
for root, _, files in os.walk(poles_data_path):
    for file in files:
        if file.endswith('_poles_types.json'):
            poles_path = os.path.join(poles_data_path, file)

            with open(poles_path, "r") as f:
                data = json.load(f)
            
            for number, type in enumerate(data, 1):
                ekran.poles[number] = Pole()
                ekran.poles[number].description_name = f'pole_{file[:-17]}_{number:03d}'
                ekran.poles[number].type = type

                
            # xxxxxxxxxxxxxx USUŃ xxxxxxxxxxxxxxxxx
                ekran.poles[number].height = 5.0
                ekran.start_higher_load_axes_number = 4
                ekran.end_higher_load_axes_number = 4
            # xxxxxxxxxxxxxx USUŃ xxxxxxxxxxxxxxxxx
            

            f.close()

# ustalenie pala (nazwy bloku) na podstawie wysokości słupa i czy słup jest wzmocniony
for pole_number, pole in ekran.poles.items():
    if pole_number <= ekran.start_higher_load_axes_number or pole_number > len(ekran.poles)-ekran.end_higher_load_axes_number:
        higher_load_pole = True
    ekran.piles[pole_number].choose_pile(pole.height, higher_load_pole)
    higher_load_pole = False
    
    # na razie jest to jednoznaczne z nazwą bloku cada - do zmiany
    ekran.piles[pole_number].acad_block_name = ekran.piles[pole_number].type
    

# przypisanie wspórzędnych do pala

for axis_number, axis in ekran.main_axes.items():
    ekran.piles[axis_number].x_coord = axis.x_coord
    ekran.piles[axis_number].y_coord = axis.y_coord
    ekran.piles[axis_number].z_coord = axis.z_coord_pile


# tworzenie obiektów paneli na podstawie lokalizacji pali

# for number, pile in enumerate(ekran.piles.values(),1):
#     if number<len(ekran.piles):
#         ekran.panels[number] = Panel()
#         ekran.panels[number].number = number
#         ekran.panels[number].description_name = pile.description_name.replace('pile', 'panel')
#         ekran.panels[number].position = pile.position
#         ekran.panels[number].end_position = ekran.piles[number+1].position
#         ekran.panels[number].calc_width() 













# tworzy obiekt "malarza" i
drawer = Drawer()

# setup rysunku
drawer.add_layers()

# rysuje profil terenu
drawer.draw_terrain(ekran.terrain_profile)

# czyści obiekty acad osi głównych - do zmiany jeśli będzie wersja okienkowa!

# ekran.clear_cad_objects(ekran.main_axes)

# rysuje osie na profilu(tabelka)
drawer.draw_axes_in_table(ekran.main_axes)

# rysuje bazę tabeli
drawer.draw_table(ekran.length)

# wstawia wartości do tabeli
drawer.draw_table_values(ekran.main_axes)

# rysuje pale na rozwinieciu
drawer.draw_piles(ekran.piles, ekran.main_axes)

# rysuje pale na planie
# drawer.draw_piles_on_plan(ekran.piles)


