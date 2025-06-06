from pyzwcad import ZwCAD, APoint
import os
import json
from classes import *
from drawer import *
import math
import copy


ekran = AcousticScreen()

ekran.description_name = 'EL01'
ekran.height = 5

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

# tworzenie obiektów pali na podstawie ich wspórzędnych

for root, _, files in os.walk(piles_data_path):
    for file in files:
        if file.endswith('_coordinates.json'):
            piles_path = os.path.join(piles_data_path, file)

            with open(piles_path, "r") as f:
                data = json.load(f)
            
            for number, position in enumerate(data, 1):
                ekran.piles[number] = Pile()
                ekran.piles[number].description_name = f'pile_{file[:-23]}_{number:03d}'

                ekran.piles[number].position = Point(x=position[0],y=position[1])
                    
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

    ekran.main_axes[number].position = pile.position
    ekran.main_axes[number].position.z = None

# przyporządkowanie osi poprzedzająch i kolejnych
for number, axis in ekran.main_axes.items():
    try:
        axis.previous_axis = ekran.main_axes[number-1]
    except:
        pass
    try:
        axis.next_axis = ekran.main_axes[number+1]
    except:
        pass

#  ustalenie odległości miedzy osiami

distance_on_profile = 0

for axis_number, axis in ekran.main_axes.items():
    axis.position.x_position_on_profile = distance_on_profile
    if axis_number<len(ekran.main_axes):
        axis.calc_next_span_length()
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

        if axis.position.x_position_on_profile>terrain_point.x_position_on_profile:
            delta_x = ekran.terrain_profile.profile[number+1].x_position_on_profile - terrain_point.x_position_on_profile
            delta_y = ekran.terrain_profile.profile[number+1].z - terrain_point.z
            axis_delta_x = axis.position.x_position_on_profile - terrain_point.x_position_on_profile
            axis.z_coord_terrain = (axis_delta_x/delta_x)*delta_y + terrain_point.z
            ekran.terrain_profile.new_tarrain_profile[axis_number] = Point(x_position_on_profile = axis.position.x_position_on_profile, 
                                                                           z = axis.z_coord_terrain)


# obliczanie rzędnych pali na osiach głównych

for axis in ekran.main_axes.values():
    axis.z_coord_pile = math.ceil(10*(axis.z_coord_terrain))/10 + ekran.min_elevation
    
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

                # na razie jest to jednoznaczne z nazwą bloku cada - do zmiany
                ekran.poles[number].acad_block_name = ekran.poles[number].type

                
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
        ekran.piles[pole_number].extension = True

    ekran.piles[pole_number].choose_pile(pole.height, higher_load_pole)
    higher_load_pole = False
    
    # na razie jest to jednoznaczne z nazwą bloku cada - do zmiany
    ekran.piles[pole_number].acad_block_name = ekran.piles[pole_number].type
    

# przypisanie wspórzędnych do pala

for axis_number, axis in ekran.main_axes.items():

    ekran.piles[axis_number].postion = axis.position
    ekran.piles[axis_number].postion.z = axis.z_coord_pile

# przypisanie pozycji dla słupów

for axis_number, axis in ekran.main_axes.items():

    ekran.poles[axis_number].position = axis.position
    ekran.poles[axis_number].position.z = axis.z_coord_pile

# tworzenie bloków podwalin

for axis_number, axis in ekran.main_axes.items():

    # jeżeli to nie jest ostatnie przęsło ani przęsło z drzwiami to
    if axis.next_span_length != None or axis.next_span_doors != False:

        ekran.ground_beams[axis_number] = GroundBeam()
        ekran.ground_beams[axis_number].number = axis.number
        ekran.ground_beams[axis_number].position = axis.position
        ekran.ground_beams[axis_number].position.z = axis.z_coord_pile
        ekran.ground_beams[axis_number].width = axis.next_span_length

# ustalenie różnicy wysokości dla wcięć podwalin i czy są poszerzenia na pale
# do zmiany tak żeby uwzgledniał poszerzenie jednostronne podwaliny

for axis_number, axis in ekran.main_axes.items():
    # jeżeli to nie jest ostatnie przęsło to
    if axis.next_span_length != None:
        ekran.ground_beams[axis_number].detla_z =round(axis.z_coord_pile - ekran.main_axes[axis_number+1].z_coord_pile, 1)
        
        if ekran.piles[axis_number].extension == True or ekran.piles[axis_number].extension == True:
            ekran.ground_beams[axis_number].extension = True

# ustalenie nazwy podwaliny (bloku) na podstawie rozpiętośc przęsła, różnicy kolejnych pali i czy pale są poszerzone
# do zmiany tak żeby uwzgledniał poszerzenie jednostronne podwaliny


for ground_beam in ekran.ground_beams.values():

    name = []

    name.append(str(int(ground_beam.width)))
    name.append(str(int(ground_beam.detla_z*10)))
    if ground_beam.extension ==True:
        name.append('P')
                
    ground_beam.acad_block_name = '_'.join(name)

# tworzenie obiektów paneli

for axis_number, axis in ekran.main_axes.items():

    # jeżeli to nie jest ostatnie przęsło to
    if axis.next_span_length != None:

        ekran.panels[axis_number] = Panel()
        ekran.panels[axis_number].number = axis.number
        ekran.panels[axis_number].position = copy.deepcopy(axis.position)
        ekran.panels[axis_number].position.z = axis.z_coord_pile
        if ekran.ground_beams[axis_number].detla_z > 0:
            ekran.panels[axis_number].position.z -= ekran.ground_beams[axis_number].detla_z

# przypisanie typu ekranu i wysokości

# zmienić żeby pobierało dane z excela
for panel in ekran.panels.values():
    panel.type = 1 
    panel.height = 5

# ustalenie nazwy panela (bloku) na podstawie wysokości słupa, rozpiętośc przęsła, typu ekanu i czy przęsło ma drzwi

for panel_number, panel in ekran.panels.items():
    name = []

    if panel.doors == True:
        name.append('DZ')
    else:
        name.append('P')

    name.append(str(int(ekran.main_axes[panel_number].next_span_length)))
    name.append(str(int(panel.height)))
    name.append(str(int(panel.type)))


    ekran.panels[panel_number].acad_block_name = '_'.join(name)













# tworzy obiekt "malarza"
drawer = Drawer()

# setup rysunku
drawer.add_layers()

# rysuje profil terenu
drawer.draw_terrain(ekran.terrain_profile)

# rysuje osie na profilu(tabelka)
drawer.draw_axes_in_table(ekran.main_axes)

# rysuje bazę tabeli
drawer.draw_table(ekran.length)

# wstawia wartości do tabeli
drawer.draw_table_values(ekran.main_axes)

# rysuje pale na rozwinieciu
drawer.draw_piles(ekran.piles)

# rysuje słupy na rozwinięciu
drawer.draw_poles(ekran.poles)

# rysuje belki podwalinowe na rozwinięciu
drawer.draw_ground_beams(ekran.ground_beams)

# rysuje panele na rozwinięciu
drawer.draw_panels(ekran.panels)


# rysuje opis nad rozwinięciem

x_pos = ekran.length//2
y_pos = ekran.piles[len(ekran.main_axes)//2].position.z + ekran.height

drawer.draw_title(ekran.description_name, x_pos, y_pos)






# rysuje wymiary

text_position = min(pile.position.z - pile.height for pile in ekran.piles.values()) - 1

dimenstion_positions = []
for axis_number, axis in ekran.main_axes.items():
    if axis.next_span_length != None:
        dimenstion_positions.append([Point(x=axis.position.x_position_on_profile, y=axis.z_coord_pile-ekran.piles[axis_number].height),
                                    Point(x=axis.next_axis.position.x_position_on_profile, y=axis.next_axis.z_coord_pile-ekran.piles[axis_number+1].height),
                                    Point(x=axis.position.x_position_on_profile, y=text_position)])


drawer.draw_dimensions(dimenstion_positions)

print('gotowe')