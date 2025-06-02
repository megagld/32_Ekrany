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


        # objects
        self.terrain_profile = None
        self.piles = None
        self.poles = None
        self.panels = None
        self.ground_beams = None

class ConstructionObject:
    def __init__(self):
        self.number = None
        self.description_name = None
        self.type = None
        self.height = None # [m]
        self.width = None
        self.position = None


    def draw(self):
        pass

class Panel(ConstructionObject):
    def __init__(self):
        super().__init__() 


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
        self.profile = None
        self.y_scale = 10

