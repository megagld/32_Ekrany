#bmystek
import pyzwcad

class Drawer:
    def __init__(self):

        self.acad = pyzwcad.ZwCAD()
        self.acad.prompt("Ekrany akustyczne - rozwiniecia\n")
        print (self.acad.doc.Name)

        self.draw_setup = []

    def draw_terrain(self, profile):

        points = []

        for point in profile.profile:
            point_x = point[0]
            point_y = point[1]//profile.y_scale
            points.append(pyzwcad.APoint(point_x, point_y))
        
        self.acad.model.AddPolyline(points)
