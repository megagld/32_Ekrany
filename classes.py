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
        
        self.main_axes = {}

        # objects
        self.terrain_profile = None
        self.piles = {}
        self.poles = None
        self.panels = {}
        self.ground_beams = None

class ConstructionObject:
    def __init__(self):
        self.number = None
        self.description_name = None
        self.type = None
        self.height = None # [m]
        self.width = None
        self.position = None
        self.cad_object = None

    def add_Z_value(self, z=0):
        if len(self.position) == 2:
            self.position.append(z)


class Panel(ConstructionObject):
    def __init__(self):
        super().__init__() 
        self.end_position = None

    def calc_width(self):
        width = ((self.position[0] - self.end_position[0])**2 + (self.position[1] - self.end_position[1])**2)**0.5
        self.width = round(width)
        if abs(self.width-width)>0.03:
            print(f'błąd rozstawienia pali - {abs(self.width-width)}')

class Pole(ConstructionObject):
    def __init__(self):
        super().__init__() 


class Pile(ConstructionObject):
    def __init__(self):
        super().__init__() 
        self.diameter = None # [m]


class GroundBeam(ConstructionObject):
    def __init__(self):
        super().__init__() 


class Terrain(ConstructionObject):
    def __init__(self):
        super().__init__() 
        self.profile = {}
        self.y_scale = 0.1

    def scale_Y_axis(self):
        for point in self.profile.values():
            point[1] = point[1]*self.y_scale

    def add_Z_values_to_terrain(self, z=0):
        for point in self.profile.values():
            if len(point) == 2:
                point.append(z)