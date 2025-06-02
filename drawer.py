#bmystek
import pyzwcad
from pyzwcad import *

class Drawer:
    def __init__(self):

        self.acad = pyzwcad.ZwCAD()
        self.acad.prompt("Ekrany akustyczne - rozwiniecia\n")
        print (self.acad.doc.Name)

        self.draw_setup = []

    def draw_terrain(self, profile):

        points = []

        for point in profile.profile.values():
            points.append(APoint(point))
        
        profile.cad_object = self.acad.model.AddPolyline(points)
        

    def draw_piles_on_plan(self, piles):

        for number, pile in piles.items():
            position = APoint(pile.position)
            text = self.acad.model.AddText(f'{pile.description_name}', position, 0.4)
            pile.cad_object = self.acad.model.AddCircle(position, pile.diameter)


        # piles[1].cad_object.Radius = 2 testowa zmiana średnicy