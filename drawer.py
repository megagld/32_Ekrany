# bmystek
import pyzwcad
from pyzwcad import *
import math
import os


class Drawer:
    def __init__(self):

        self.acad = pyzwcad.ZwCAD()

        self.acad.prompt("Ekrany akustyczne - rozwiniecia\n")
        print(self.acad.doc.Name)

        self.draw_setup = []

    def draw_terrain(self, terrain_profile):

        points = []

        for point in terrain_profile.profile.values():
            points.append(APoint(point.x_position_on_profile, point.z, 0))

        terrain_profile.cad_object = self.acad.model.AddPolyline(points)
        terrain_profile.cad_object.layer = 'm_teren_pierwotny'
        terrain_profile.cad_object.color = 256
        terrain_profile.cad_object.linetypescale = 0.1

        points = []

        for point in terrain_profile.new_tarrain_profile.values():
            points.append(APoint(point.x_position_on_profile, point.z, 0))

        terrain_profile.cad_object = self.acad.model.AddPolyline(points)
        terrain_profile.cad_object.layer = 'm_teren'
        terrain_profile.cad_object.color = 3

    def draw_piles_on_plan(self, piles):

        for pile in piles.values():
            position = APoint(pile.position.x, pile.position.y)
            text = self.acad.model.AddText(
                f'{pile.description_name}', position, 0.4)
            pile.cad_object = self.acad.model.AddCircle(
                position, pile.diameter)

    def draw_piles(self, piles):

        for number, pile in piles.items():
            position = APoint(pile.position.x_position_on_profile,
                              pile.position.z)
            pile.cad_object = self.acad.model.InsertBlock(position,
                                                          pile.acad_block_name,
                                                          1, 1, 1, 0)
            pile.cad_object.layer = 'm_pale'
            pile.cad_object.color = 256

    def draw_panels(self, panels):

        for number, panel in panels.items():
            position = APoint(panel.position.x_position_on_profile,
                              panel.position.z)
            panel.cad_object = self.acad.model.InsertBlock(position,
                                                          panel.acad_block_name,
                                                          1, 1, 1, 0)
            panel.cad_object.layer = 'm_panele'
            panel.cad_object.color = 256

    def draw_ground_beams(self, ground_beams):

        for number, ground_beam in ground_beams.items():
            position = APoint(ground_beam.position.x_position_on_profile,
                              ground_beam.position.z)
            ground_beam.cad_object = self.acad.model.InsertBlock(position,
                                                          ground_beam.acad_block_name,
                                                          1, 1, 1, 0)
            ground_beam.cad_object.layer = 'm_podwaliny'
            ground_beam.cad_object.color = 256

    def draw_poles(self, poles):

        for number, pole in poles.items():
            position = APoint(pole.position.x_position_on_profile,
                              pole.position.z)
            pole.cad_object = self.acad.model.InsertBlock(position,
                                                          pole.acad_block_name,
                                                          1, 1, 1, 0)
            pole.cad_object.layer = 'm_slupy'
            pole.cad_object.color = 256

    def draw_axes_in_table(self, main_axes):
        for number, axis in main_axes.items():

            point_1 = APoint(axis.position.x_position_on_profile, 0)
            point_2 = APoint(axis.position.x_position_on_profile, 8)
            point_3 = APoint(axis.position.x_position_on_profile, 8.75, 0)
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

        self.acad.doc.ActiveLayer = self.acad.doc.Layers['m_tabelka']
        # for i in self.acad.doc.Colors:
        #     print(i)
        # # self.acad.doc.ActiveColor = 10




        # self.acad.Regen = True

        # print(self.acad.Color)


        text_height = 0.5

        for axis in main_axes.values():

            point_1 = APoint(axis.position.x_position_on_profile - 0.3, 0.2)
            point_2 = APoint(axis.position.x_position_on_profile - 0.3, 2.7)
            point_3 = APoint(axis.position.x_position_on_profile - 0.3, 5.2)

            text = self.acad.model.AddText(
                f'{axis.position.x_position_on_profile:.1f}', point_1, text_height)
            text.Alignment = 12
            text.color = 256
            text.rotation = math.pi/2
            axis.cad_objects.append(text)

            text = self.acad.model.AddText(
                f'{axis.z_coord_terrain:.2f}', point_2, text_height)
            text.Alignment = 12
            text.color = 256
            text.rotation = math.pi/2
            axis.cad_objects.append(text)

            text = self.acad.model.AddText(
                f'{axis.z_coord_pile:.2f}', point_3, text_height)
            text.Alignment = 12
            text.color = 1
            text.rotation = math.pi/2
            axis.cad_objects.append(text)

    def draw_title(self, descriptions):
            
            self.acad.doc.ActiveLayer = self.acad.doc.Layers['m_tekst']

            point_1 = APoint(descriptions.main_dercription_position.x_position_on_profile,
                              descriptions.main_dercription_position.z + 4)
            point_2 = APoint(descriptions.main_dercription_position.x_position_on_profile,
                              descriptions.main_dercription_position.z + 2.5)

            text_height = 1
            text_1 = self.acad.model.AddText(
                descriptions.main_dercription, point_1, text_height)
            text_1.Alignment = 4
            text_1.color = 256

            text_height = 0.75
            text_2 = self.acad.model.AddText(
                '%%Uskala 1:200', point_2, text_height)
            text_2.Alignment = 4
            text_2.color = 1

            descriptions.cad_objects.append(text_1)
            descriptions.cad_objects.append(text_2)

    def draw_dimensions(self, descriptions):
            
        self.acad.doc.ActiveLayer = self.acad.doc.Layers['m_wymiary']
        self.acad.doc.ActiveDimStyle = self.acad.doc.DimStyles['CDM-ME200ME']
        # self.acad.doc.CurrentColor = 256 ?????
        
        for dimension in descriptions.dimenstions:
            point_1 = APoint(dimension[0].x, dimension[0].y)
            point_2 = APoint(dimension[1].x, dimension[1].y)
            point_3 = APoint(dimension[2].x, dimension[2].y)

            dimension = self.acad.model.AddDimRotated(point_1,point_2,point_3,0)
            dimension.color = 256
            descriptions.cad_objects.append(dimension)
            
    def add_layers(self):

        layers_setup = [('m_tekst', 2, 'continuous'),
                        ('m_tabelka', 1, 'continuous'),
                        ('m_wymiary', 1, 'continuous'),
                        ('m_pale', 1, 'continuous'),
                        ('m_slupy', 7, 'continuous'),
                        ('m_podwaliny', 8, 'continuous'),
                        ('m_panele', 7, 'continuous'),
                        ('m_teren', 1, 'continuous'),
                        ('m_zestwienie', 1, 'continuous'),
                        ('m_teren_pierwotny', 6, 'hidden')]

        for layer, color, linetype in layers_setup:
            if layer not in (layer.name for layer in self.acad.doc.Layers):
                tmp = self.acad.doc.Layers.Add(layer)
                tmp.color = color
                tmp.Linetype = linetype

    def add_layout(self, layout_name):
        if layout_name not in (layout.Name for layout in self.acad.doc.Layouts):
            layout = self.acad.doc.Layouts.Add(layout_name)
        
            self.acad.doc.ActiveLayout = layout