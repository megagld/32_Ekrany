#bmystek
import pyzwcad
from pyzwcad import *
import math
import os

class Drawer:
    def __init__(self):

        self.acad = pyzwcad.ZwCAD()
        self.acad.prompt("Ekrany akustyczne - rozwiniecia\n")
        print (self.acad.doc.Name)

        self.draw_setup = []

    def draw_terrain(self, terrain_profile):

        points = []

        for point in terrain_profile.profile.values():
            points.append(APoint(point.x_position_on_profile, point.z, 0))
        
        terrain_profile.cad_object = self.acad.model.AddPolyline(points)
        terrain_profile.cad_object.layer = 'm_teren_pierwotny'
        terrain_profile.cad_object.color= 257
        terrain_profile.cad_object.linetypescale = 0.1
        
        points = []

        for point in terrain_profile.new_tarrain_profile.values():
            points.append(APoint(point.x_position_on_profile, point.z, 0))
        
        terrain_profile.cad_object = self.acad.model.AddPolyline(points)
        terrain_profile.cad_object.layer = 'm_teren'
        terrain_profile.cad_object.color= 3

    def draw_piles_on_plan(self, piles):

        for number, pile in piles.items():
            position = APoint(pile.position)
            text = self.acad.model.AddText(f'{pile.description_name}', position, 0.4)
            pile.cad_object = self.acad.model.AddCircle(position, pile.diameter)


    def draw_piles(self, piles, axes):

        for number, pile in piles.items():
            position = APoint(axes[number].distance_on_profile, pile.z_coord)
            pile.cad_object = self.acad.model.InsertBlock(position, 
                                                          pile.acad_block_name,
                                                          1,
                                                          1,
                                                          1,
                                                          0)
            pile.cad_object.layer = 'm_pale'
            pile.cad_object.color = 257

    def draw_axes_in_table(self, main_axes):
        for number, axis in main_axes.items():

            point_1 = APoint(axis.distance_on_profile, 0)
            point_2 = APoint(axis.distance_on_profile, 8)
            point_3 = APoint(axis.distance_on_profile, 8.75,0)
            radius = 0.75
            text_height = 0.6
            
            text = self.acad.model.AddText(str(number), point_3, text_height)
            text.Alignment = 10
            text.layer = 'm_tabelka'
            text.color = 1

            circle = self.acad.model.AddCircle(point_3, radius)
            circle.layer = 'm_tabelka'
            circle.color = 8

            line = self.acad.model.AddLine(point_1, point_2)
            line.layer = 'm_tabelka'
            line.color = 8

    def draw_table(self, length):

        main_text = ['Odległość [m]',
                     'Rzędna terenu [m npm.]',
                     'Rzędna góry pala [m npm.]']
        
        text_height = 0.8

        
        for row, text in enumerate(main_text):
            point_1 = APoint(-16, row * 2.5)
            point_2 = APoint(length, row * 2.5)
            line = self.acad.model.AddLine(point_1, point_2)
            line.layer = 'm_tabelka'
            line.color = 8

            point_3 = APoint(-15, 0.2 + row * 2.5)

            text = self.acad.model.AddText(text, point_3, text_height)
            text.Alignment = 12
            text.layer = 'm_tabelka'
            text.color = 1

    def draw_table_values(self, main_axes):
        text_height = 0.5
                
        for number, axis in main_axes.items():

            point_1 = APoint(axis.distance_on_profile - 0.2 , 0.2)
            point_2 = APoint(axis.distance_on_profile - 0.2 , 2.7)
            point_3 = APoint(axis.distance_on_profile - 0.2 , 5.2)

            text = self.acad.model.AddText(f'{axis.distance_on_profile:.1f}', point_1, text_height)
            text.Alignment = 12
            text.layer = 'm_tabelka'
            text.color = 1
            text.rotation = math.pi/2
            axis.cad_objects.append(text)

            text = self.acad.model.AddText(f'{axis.terrain_z_position:.2f}', point_2, text_height)
            text.Alignment = 12
            text.layer = 'm_tabelka'
            text.color = 1
            text.rotation = math.pi/2
            axis.cad_objects.append(text)

            text = self.acad.model.AddText(f'{axis.z_coord_pile:.2f}', point_3, text_height)
            text.Alignment = 12
            text.layer = 'm_tabelka'
            text.color = 1
            text.rotation = math.pi/2
            axis.cad_objects.append(text)





    def add_layers(self):

        layers_setup =[('m_tekst',2,'continuous'),
                        ('m_tabelka',1,'continuous'),
                        ('m_wymiary',1,'continuous'),
                        ('m_pale',1,'continuous'),
                        ('m_slupy',7,'continuous'),
                        ('m_podwaliny',8,'continuous'),
                        ('m_panele',7,'continuous'),
                        ('m_teren',1,'continuous'),
                        ('m_zestwienie',1,'continuous'),
                        ('m_teren_pierwotny',6,'hidden') ]

        for layer, color, linetype in layers_setup:
            if layer not in (layer.name for layer in self.acad.doc.Layers):
                tmp = self.acad.doc.Layers.Add(layer)
                tmp.color = color
                tmp.Linetype = linetype

