#bmystek
from pyzwcad import ZwCAD, APoint
import pyzwcad
import os
import json
from classes import *
from drawer import *
import math
import copy

class AcousticScreen:
    def __init__(self):
        # main data
        self.number = None
        self.description_name = None
        self.height = None # [m]
        self.type = None
        self.terain_milage_dalay = 0 # [m]
        self.first_axis_number = None # do zmiany!!!!!!!!!! bo z excela pobiera '-'
        self.mileage_delay = None # [km] # do zmiany!!!!!!!!!! bo z excela pobiera '-'
        self.previous_screen = None
        self.next_screen = None
        self.start_higher_load_axes_number = None
        self.end_higher_load_axes_number = None

        self.doors_position = None

        # self.start_position_dalay = 0 #[m]  ?????? po co to
        self.min_elevation = 0.05 # [m]
        self.length = None
        
        # objects
        self.terrain_profile = None
        self.main_axes = {}

        self.piles = {}
        self.poles = {}
        self.panels = {}
        self.ground_beams = {}

        self.descriptions = None

    def get_terrain_data(self, data):
        # pobranie danych profilu terenu
        
        self.terrain_profile = Terrain()
        self.terrain_profile.description_name = f'terrain_{self.description_name}'
        for number, point_data in enumerate(data, 1):
            x_position_on_profile = point_data[0]
            z = point_data[1]
            self.terrain_profile.profile[number] = Point(z=z, 
                                                        x_position_on_profile = x_position_on_profile)

        # przeskalowanie na osi Z
        self.terrain_profile.scale_Z_axis()
        # przesunięcie terenu na profilu wzgledem pali
        self.terrain_profile.move_terrain_horizontaly(self.terain_milage_dalay)

    def get_piles_data(self, data):
        # tworzenie obiektów pali na podstawie ich wspórzędnych

        for number, position in enumerate(data):
            axis_numer = number + self.first_axis_number

            self.piles[axis_numer] = Pile()
            self.piles[axis_numer].number = axis_numer
            self.piles[axis_numer].description_name = f'pile_{self.description_name}_{axis_numer:03d}'
            self.piles[axis_numer].position = Point(x=position[0],
                                                y=position[1])

    def get_poles_data(self, data):
        # tworzenie obiektów słupów i ustalenie ich wysokości
        # na razie analogicznie do starego skryptu - tj. ręcznie

        for number, type in enumerate(data):
            axis_numer = number + self.first_axis_number
            
            self.poles[axis_numer] = Pole()
            self.poles[axis_numer].number = axis_numer
            self.poles[axis_numer].description_name = f'pole_{self.description_name}_{axis_numer:03d}'
            self.poles[axis_numer].type = type

            # na razie jest to jednoznaczne z nazwą bloku cada - do zmiany
            self.poles[axis_numer].acad_block_name = self.poles[axis_numer].type
            self.poles[axis_numer].height = self.height
                
    def make(self):

        # pobiera pliki z katalogu _data i podkatalogów
        input_dir = os.getcwd()
        project_data_dir = '{}\\{}'.format(input_dir, '_project')


        # ustalenie przesunięcia pala wzgledem profilu rozwiniecia terenu
        # oznacza w którym miejscu na profilu terenu jest pierwsza oś    

        # pobranie danych profilu terenu

        

        # przesunięcie poziome terenu ???? powtórzone?

        # self.terrain_profile.move_terrain_horizontaly(self.terain_milage_dalay)
        

        # ustalenie głównych osi przęseł

        # tworzenie osi głównych na podstawie współrzędnych pali

        for number, pile in enumerate(self.piles.values()):
            axis_numer = number + self.first_axis_number

            self.main_axes[axis_numer] = MainAxis()

            self.main_axes[axis_numer].number = axis_numer
            self.main_axes[axis_numer].description_name = pile.description_name.replace('pile', 'axis')

            self.main_axes[axis_numer].position = pile.position
            self.main_axes[axis_numer].position.z = None

        # przyporządkowanie osi poprzedzająch i kolejnych
        for axis in self.main_axes.values():
            try:
                axis.previous_axis = self.main_axes[axis.number-1]
            except:
                pass
            try:
                axis.next_axis = self.main_axes[axis.number+1]
            except:
                pass

        #  ustalenie odległości miedzy osiami

        distance_on_profile = 0

        for axis_number, axis in self.main_axes.items():
            axis.position.x_position_on_profile = distance_on_profile
            try:
                axis.calc_next_span_length()
                distance_on_profile += axis.next_span_length
            except:
                pass
                
        # ustalenie długości selfu na profilu
        self.length = distance_on_profile

        # Sprawdzenie czy osie nie są poza dostępnym profilem terenu
        if any((self.terrain_profile.profile[1].x_position_on_profile > 0,
            self.terrain_profile.profile[max(self.terrain_profile.profile)].x_position_on_profile < self.length)):
            print('brakuje profilu terenu')

        # oblicznie rzędnych terenu w osiach głównych

        for axis in self.main_axes.values():

            for number, terrain_point in self.terrain_profile.profile.items():

                if axis.position.x_position_on_profile>terrain_point.x_position_on_profile:
                    delta_x = self.terrain_profile.profile[number+1].x_position_on_profile - terrain_point.x_position_on_profile
                    delta_y = self.terrain_profile.profile[number+1].z - terrain_point.z
                    axis_delta_x = axis.position.x_position_on_profile - terrain_point.x_position_on_profile
                    axis.z_coord_terrain = (axis_delta_x/delta_x)*delta_y + terrain_point.z
                    self.terrain_profile.new_tarrain_profile[axis.number] = Point(x_position_on_profile = axis.position.x_position_on_profile, 
                                                                                z = axis.z_coord_terrain)

        # ustalenie poziomu terenu dla przęseł z drzwiami (poziom pali i terenu w przęśle ma być ten sam)

        for axis in self.main_axes.values():
            if axis.number in self.doors_position:
                axis.next_axis.z_coord_terrain = axis.z_coord_terrain
                self.terrain_profile.new_tarrain_profile[axis.next_axis.number].z = axis.next_axis.z_coord_terrain
        
        # obliczanie rzędnych pali na osiach głównych

        for axis in self.main_axes.values():
            axis.z_coord_pile = math.ceil(10*(axis.z_coord_terrain))/10 + self.min_elevation
                    
        # ustalenie pala (nazwy bloku) na podstawie wysokości słupa i czy słup jest wzmocniony
        for pole in self.poles.values():
            
            if pole.number <= self.start_higher_load_axes_number or pole.number > len(self.poles)+self.first_axis_number-1:
                higher_load_pole = True
            else:
                higher_load_pole = False


            self.piles[pole.number].choose_pile(pole.height, higher_load_pole)

            
            # na razie jest to jednoznaczne z nazwą bloku cada - do zmiany
            self.piles[pole.number].acad_block_name = self.piles[pole.number].type
            
        # przypisanie wspórzędnych do pala

        for axis in self.main_axes.values():

            self.piles[axis.number].postion = axis.position
            self.piles[axis.number].postion.z = axis.z_coord_pile

        # przypisanie pozycji dla słupów

        for axis in self.main_axes.values():

            self.poles[axis.number].position = axis.position
            self.poles[axis.number].position.z = axis.z_coord_pile

        # tworzenie bloków podwalin

        for axis in self.main_axes.values():

            # jeżeli to nie jest ostatnie przęsło ani przęsło z drzwiami to
            if axis.next_span_length != None or axis.next_span_doors != False:

                self.ground_beams[axis.number] = GroundBeam()
                self.ground_beams[axis.number].number = axis.number
                self.ground_beams[axis.number].position = axis.position
                self.ground_beams[axis.number].position.z = axis.z_coord_pile
                self.ground_beams[axis.number].width = axis.next_span_length

        # ustalenie różnicy wysokości dla wcięć podwalin i czy są poszerzenia na pale albo szerokie pale
        # do zmiany tak żeby uwzgledniał poszerzenie jednostronne podwaliny

        for axis in self.main_axes.values():
            # jeżeli to nie jest ostatnie przęsło to
            if axis.next_span_length != None:
                self.ground_beams[axis.number].detla_z =round(axis.z_coord_pile - axis.next_axis.z_coord_pile, 1)
                
                if any((self.piles[axis.number].extension == True,
                        self.piles[axis.number+1].extension == True,
                        self.piles[axis.number].head_diameter == 0.8,
                        self.piles[axis.number+1].head_diameter == 0.8)):

                    self.ground_beams[axis.number].extension = True

        # ustalenie nazwy podwaliny (bloku) na podstawie rozpiętośc przęsła, różnicy kolejnych pali i czy pale są poszerzone
        # do zmiany tak żeby uwzgledniał poszerzenie jednostronne podwaliny


        for ground_beam in self.ground_beams.values():

            name = []

            name.append(str(int(ground_beam.width)))
            name.append(str(int(ground_beam.detla_z*10)))
            if ground_beam.extension ==True:
                name.append('P')
                        
            ground_beam.acad_block_name = '_'.join(name)

        # tworzenie obiektów paneli

        for axis in self.main_axes.values():

            # jeżeli to nie jest ostatnie przęsło to
            if axis.next_span_length != None:

                self.panels[axis.number] = Panel()
                self.panels[axis.number].number = axis.number
                self.panels[axis.number].position = copy.deepcopy(axis.position)
                self.panels[axis.number].position.z = axis.z_coord_pile
                if self.ground_beams[axis.number].detla_z > 0:
                    self.panels[axis.number].position.z -= self.ground_beams[axis.number].detla_z

        # przypisanie typu ekranu i wysokości

        for panel in self.panels.values():
            panel.type = self.type 
            panel.height = self.height

        # przypisanie do obiektów paneli informacji czy są drzwi

        for axis_number in self.doors_position:
            self.panels[axis_number].doors = True

        # ustalenie nazwy panela (bloku) na podstawie wysokości słupa, rozpiętośc przęsła, typu ekanu i czy przęsło ma drzwi

        for panel in self.panels.values():
            name = []

            if panel.doors == True:
                name.append('DZ')
            else:
                name.append('P')

            name.append(str(int(self.main_axes[panel.number].next_span_length)))
            name.append(str(int(panel.height)))
            name.append(str(int(panel.type)))


            self.panels[panel.number].acad_block_name = '_'.join(name)


        # tworzenie opisów
        self.descriptions = Descriptions()

        # opis główny

        self.descriptions.main_dercription = f'%%UEKRAN AKUSTYCZNY {self.description_name}'

        x_position_on_profile = self.length//2
        z = self.piles[len(self.main_axes)//2].position.z + self.height

        self.descriptions.main_dercription_position = Point(x_position_on_profile=x_position_on_profile, z = z)

        # linie wymiarowe

        text_position = min(pile.position.z - pile.height for pile in self.piles.values()) - 1

        self.dimenstions_text_z_position = text_position

        for axis in self.main_axes.values():
            if axis.next_span_length != None:
                self.descriptions.dimenstions.append([Point(x=axis.position.x_position_on_profile,
                                                            y=axis.z_coord_pile-self.piles[axis.number].height),
                                                    Point(x=axis.next_axis.position.x_position_on_profile,
                                                            y=axis.next_axis.z_coord_pile-self.piles[axis.number+1].height),
                                                    Point(x=axis.position.x_position_on_profile,
                                                            y=text_position)])


    def draw_profil(self):
        # tworzy obiekt "malarza"
        drawer = Drawer()

        # setup rysunku
        drawer.add_layers()

        # rysuje profil terenu
        drawer.draw_terrain(self.terrain_profile)

        # rysuje pale na rozwinieciu
        drawer.draw_piles(self.piles)

        # rysuje słupy na rozwinięciu
        drawer.draw_poles(self.poles)

        # rysuje belki podwalinowe na rozwinięciu
        drawer.draw_ground_beams(self.ground_beams)

        # rysuje panele na rozwinięciu
        drawer.draw_panels(self.panels)

        # rysuje osie na profilu(tabelka)
        drawer.draw_axes_in_table(self.main_axes)

        # rysuje bazę tabeli
        drawer.draw_table(self.length)

        # wstawia wartości do tabeli
        drawer.draw_table_values(self.main_axes)

        # rysuje opis nad rozwinięciem
        drawer.draw_title(self.descriptions)

        # rysuje wymiary
        drawer.draw_dimensions(self.descriptions)

        print('gotowe')








class ConstructionObject:
    def __init__(self):
        self.number = None
        self.description_name = None
        self.type = None
        self.height = None # [m]
        self.width = None

        self.position = Point()

        self.cad_objects = []
        self.acad_block_name = None

    def clear_cad_objects(self):
        for cad_object in self.cad_objects:
                print(cad_object)
                cad_object.Delete()


class Panel(ConstructionObject):
    def __init__(self):
        super().__init__() 
        self.doors = False


class Pole(ConstructionObject):
    def __init__(self):
        super().__init__() 


class Pile(ConstructionObject):
    def __init__(self):
        super().__init__() 
        self.diameter = None # [m]
        self.head_diameter = None # [m]
        self.extension = False

    def choose_pile(self, pole_height, higher_load_pole= False):
        # dobiera pal na podstawie wysokości ekranu - do rozbudowania
        # dodaje tez dłogośc słup - też do rozubudy
        piles_type_data = {2    : 'P1',
                           2.5  : 'P2',
                           3    : 'P3',
                           3.5	: 'P4',
                           4	: 'P5',
                           5	: 'P6',
                           6	: 'P7',
                           6.5	: 'P8',
                           7	: 'P9',
                           7.5	: 'P10',
                           8	: 'P11'}
        
        piles_height_data = {2   : 3,
                             2.5 : 3.5,
                             3   : 4,
                             3.5 : 4,
                             4   : 4.5,
                             5   : 5,
                             6   : 5.5,
                             6.5 : 6,
                             7   : 6,
                             7.5 : 6.5,
                             8   : 7}
        
        piles_diameter_data = {2: 0.6,
                               2.5: 0.6,
                               3: 0.6,
                               3.5: 0.6,
                               4: 0.6,
                               5: 0.6,
                               6: 0.6,
                               6.5: 0.6,
                               7: 0.8,
                               7.5: 0.8,
                               8: 0.8}

        piles_head_diameter_data = {2: 0.6,
                                           2.5: 0.6,
                                           3: 0.6,
                                           3.5: 0.6,
                                           4: 0.6,
                                           5: 0.6,
                                           6: 0.8,
                                           6.5: 0.8,
                                           7: 0.8,
                                           7.5: 0.8,
                                           8: 0.8}
        
        # jeśli słup jest być wzmocniony - zwiększa to pal o jedną pozycję wg szeregu - metoda do rozbudowania
        if higher_load_pole:
            pole_height+=1

        self.type = piles_type_data[pole_height]
        self.height = piles_height_data[pole_height]
        self.diameter = piles_diameter_data[pole_height]
        self.head_diameter = piles_head_diameter_data[pole_height]

class GroundBeam(ConstructionObject):
    def __init__(self):
        super().__init__() 
        self.detla_z = None
        self.extension = False


class Terrain(ConstructionObject):
    def __init__(self):
        super().__init__() 
        self.profile = {}
        self.new_tarrain_profile = {}
        self.z_scale = 0.1


    def scale_Z_axis(self):
        for point in self.profile.values():
            point.z *= self.z_scale
        
    def move_terrain_horizontaly(self, terain_milage_dalay):
        # teren jest przesunięty poziomo tak żeby pierwsza oś była w x = 0
        delta_x = terain_milage_dalay + self.profile[1].x_position_on_profile

        for point in self.profile.values():
            point.x_position_on_profile -= delta_x


class MainAxis:
    def __init__(self):
        self.number = None
        self.description_name = None

        self.previous_axis = None
        self.next_axis = None

        self.position = Point()  # z=0

        self.next_span_length = None

        self.next_span_doors = False

        self.z_coord_terrain = None        
        self.z_coord_pile = None

        self.cad_objects = []

    def calc_next_span_length(self):
        if self.next_axis != None:
            next_span_length = ((self.position.x - self.next_axis.position.x)**2 + (self.position.y - self.next_axis.position.y)**2)**0.5
            self.next_span_length = round(next_span_length)
            if abs(self.next_span_length-next_span_length)>0.03:
                print(f'błąd rozstawienia pali - {abs(self.next_span_length-next_span_length)}')
                print(self.number)
                
    def clear_cad_objects(self):
        for cad_object in self.cad_objects:
                cad_object.Delete()


class Point:
    def __init__(self, x=None, y=None, z=None, x_position_on_profile = None):
        self.x = x
        self.y = y
        self.z = z
        self.x_position_on_profile = x_position_on_profile


class Descriptions:
    def __init__(self):
        self.main_dercription = None
        self.main_dercription_position = None

        self.dimenstions = []
        self.dimenstions_text_z_position = None

        self.cad_objects = []
