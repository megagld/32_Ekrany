#bmystek
from pyzwcad import ZwCAD, APoint
import pyzwcad


class AcousticScreen:
    def __init__(self):
        # main data
        self.number = None
        self.description_name = None
        self.height = None # [m]
        self.type = None
        self.mileage = None # [km]
        self.start_pole_number = 1
        self.start_position_dalay = 0 #[m]
        self.terain_milage_dalay = 0 # [m]
        self.min_elevation = 0.05 # [m]
        self.length = None

        self.start_higher_load_axes_number = 0
        self.end_higher_load_axes_number = 0
        

        # objects
        self.terrain_profile = None
        self.main_axes = {}

        self.piles = {}
        self.poles = {}
        self.panels = {}
        self.ground_beams = {}

    def clear_cad_objects(self, objects):
        #do poprawy, bo nie kasuje wszystkiego
        for object in objects.values():
            for cad_object in object.cad_objects:
                print(cad_object)
                cad_object.Delete()
 

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
                           6.5	: 'P8_P',
                           7	: 'P9_P',
                           7.5	: 'P10_P',
                           8	: 'P11_P'}
        
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
        
        # jeśli słup jest być wzmocniony - zwiększa to pal o jedną pozycję wg szeregu - metoda do rozbudowania
        if higher_load_pole:
            pole_height+=1

        self.type = piles_type_data[pole_height]
        self.height = piles_height_data[pole_height]





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
