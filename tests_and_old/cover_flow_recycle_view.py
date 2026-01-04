#where to get album cover art in high quality: https://covers.musichoarders.xyz/
#Recycle view kann das was ich ungefähr möchte - viele bilder laden ein paar widgets vorbehalten und dann die bilder in den widgets austauschen -> bilder werden einmal geladen und es müssen nur eine handvoll
#widgets initiiert werden
#Imports
import glob
import os
import math


from kivy.config import Config

#Settings - config muss zuerst gesetzt werden
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'resizable', False) # Optional: Verhindert das Skalieren

#restlichen Kivy importe
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Mesh, Translate, PushMatrix, PopMatrix
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.properties import ListProperty
from kivy.cache import Cache
#from kivy.uix.image import Image




#from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
Window.borderless = True
#Window.size = (400, 900)

from kivy.graphics import RenderContext, Color, Rectangle, BindTexture
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock


from kivy.core.image import Image





"""
standart cover größe definieren -> können vertices für die winkel berechnet werden
distanzen für die unterschiedlichen Positionen definieren
Positionene definieren
winkel für die Positionen definieren
"""

 

class AccuratePerspective(Widget):
    image_source = StringProperty('')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ########Widerverwendete Variablen                  damit so wenig variablen neu definiert werden müssen wie möglich, definiere ich hier einige, die dann den Funktionen übergeben werden
        self.standard_side_length = 200 #in pixel -> ein programm schreiben, welches alle bilder öffent und dann auf eine Pixelgröße hoch bzw. runter skaliert. Diese dann unter anderem Namen abspeichern, oder unter anderem Ordner, in dem dann gesucht wird
        self.vertices_1 = [
                self.standard_side_length, 0,                           0, 0,  # Unten Links
                self.standard_side_length, 0,                           1, 0,  # Unten Rechts
                0, self.standard_side_length,                           0, 1,  # Oben Links
                self.standard_side_length, self.standard_side_length,   1, 1   # Oben Rechts

        ]

        self.default_distance = 100
        self.new_sidelength_diff_by_half = 0 #muss später wenn man die richtigen settings gefunden hat eigentliche auch nicht immer aufs neue berechnet werden

        with self.canvas:
            PushMatrix()  # Aktuellen Zustand speichern

            # HIER wird die Position festgelegt: (x, y)
            self.pos_transformation = Translate(750, 750)

            # Start-Koordinaten (Trapez 1)
            self.mesh = Mesh(
                vertices =      self.vertices_1,
                indices =       [0, 1, 2, 3],
                mode =          'triangle_strip',
                texture =       Image(image_path).texture
            )

            PopMatrix()

    def change_position(self, new_x, new_y):
        """Verschiebt das gesamte Mesh an eine neue Koordinate."""
        self.pos_transformation.x = new_x
        self.pos_transformation.y = new_y

    def change_perspective(self, richtung= 'vor', new_angle_deg = 0, new_distance = 100):

        new_angle = math.radians(new_angle_deg)
        #je nach dem, ob sich das widget ober oder unethalb des "Mittelbildes" befindet, bleiben die oberen oder unteren Ecken gleich
        self.entfernungs_skalierungsfaktor = self.default_distance/new_distance
        self.new_sidelength_diff_by_half = round((self.standard_side_length - (self.standard_side_length * self.default_distance)/new_distance)/2) # durch die enfernung


        self.delta_h = round(self.standard_side_length*(1-math.cos(new_angle)) * self.entfernungs_skalierungsfaktor)
        self.dist_durch_neigung = math.sin(new_angle) * self.standard_side_length
        self.delta_b = round(self.standard_side_length*0.5*(1-self.default_distance/(self.default_distance + self.dist_durch_neigung)))

        if richtung == 'vor':


            #unten Links
            self.unten_links_x = self.new_sidelength_diff_by_half                                   + self.delta_h
            self.unten_links_y = self.new_sidelength_diff_by_half                                   + self.delta_h

            #unten rechts
            self.unten_rechts_x = self.standard_side_length - self.new_sidelength_diff_by_half      - self.delta_h
            self.unten_rechts_y = self.new_sidelength_diff_by_half                                  + self.delta_h

            #oben links
            self.oben_links_x = self.new_sidelength_diff_by_half                                    
            self.oben_links_y = self.standard_side_length - self.new_sidelength_diff_by_half        

            #oben rechts
            self.oben_rechts_x = self.standard_side_length - self.new_sidelength_diff_by_half       
            self.oben_rechts_y = self.standard_side_length - self.new_sidelength_diff_by_half       

            self.vertices_1 = [
                self.oben_links_x,          self.oben_links_y,          0, 0,  # Oben Links
                self.oben_rechts_x,         self.oben_rechts_y,         1, 0,  # Oben Rechts
                self.unten_links_x,         self.unten_links_y,         0, 1,  # Unten Links
                self.unten_rechts_x,        self.unten_rechts_y,        1, 1   # Unten Rechts
            ]


            print(self.vertices_1)

        elif richtung == 'zurueck':
            #unten Links
            self.unten_links_x = self.new_sidelength_diff_by_half                                   
            self.unten_links_y = self.new_sidelength_diff_by_half                                   

            #unten rechts
            self.unten_rechts_x = self.standard_side_length - self.new_sidelength_diff_by_half      
            self.unten_rechts_y = self.new_sidelength_diff_by_half                                  

            #oben links
            self.oben_links_x = self.new_sidelength_diff_by_half                                    + self.delta_h                                   
            self.oben_links_y = self.standard_side_length - self.new_sidelength_diff_by_half        - self.delta_h   

            #oben rechts
            self.oben_rechts_x = self.standard_side_length - self.new_sidelength_diff_by_half       - self.delta_h   
            self.oben_rechts_y = self.standard_side_length - self.new_sidelength_diff_by_half       - self.delta_h       

            self.vertices_1 = [
                self.oben_links_x,          self.oben_links_y,          0, 0,  # Oben Links
                self.oben_rechts_x,         self.oben_rechts_y,         1, 0,  # Oben Rechts
                self.unten_links_x,         self.unten_links_y,         0, 1,  # Unten Links
                self.unten_rechts_x,        self.unten_rechts_y,        1, 1   # Unten Rechts
            ]
        
        else:
            #unten Links
            self.unten_links_x = self.new_sidelength_diff_by_half                                   
            self.unten_links_y = self.new_sidelength_diff_by_half                                   

            #unten rechts
            self.unten_rechts_x = self.standard_side_length - self.new_sidelength_diff_by_half      
            self.unten_rechts_y = self.new_sidelength_diff_by_half                                  

            #oben links
            self.oben_links_x = self.new_sidelength_diff_by_half                                                                       
            self.oben_links_y = self.standard_side_length - self.new_sidelength_diff_by_half           

            #oben rechts
            self.oben_rechts_x = self.standard_side_length - self.new_sidelength_diff_by_half  
            self.oben_rechts_y = self.standard_side_length - self.new_sidelength_diff_by_half      

            self.vertices_1 = [
                self.oben_links_x,          self.oben_links_y,          0, 0,  # Oben Links
                self.oben_rechts_x,         self.oben_rechts_y,         1, 0,  # Oben Rechts
                self.unten_links_x,         self.unten_links_y,         0, 1,  # Unten Links
                self.unten_rechts_x,        self.unten_rechts_y,        1, 1   # Unten Rechts
            ]           

        self.mesh.vertices = self.vertices_1

    def change_texture(self, image_path):
        self.mesh.texture = Image(image_path).texture

Cache.register('kv.image', limit=50)

class AlbumView(RecycleView):
    def __init__(self, **kwargs):
        super(AlbumView, self).__init__(**kwargs)
        # Wir simulieren 1000 Alben. 
        # In der Realität würdest du hier deine Ordner scannen.
        self.image_paths = self.find_image_files_multiple_globs('Music_Library')

        self.data = [
            {
                'image_source': self.image_paths[i],

            } 
            for i in range(len(self.image_paths))
        ]

    def find_image_files_multiple_globs(self, directory):
        # Definieren Sie die Muster für jede Endung
        jpg_pattern = os.path.join(directory, "**/*.jpg")
        jpeg_pattern = os.path.join(directory, "**/*.jpeg")
        png_pattern = os.path.join(directory, "**/*.png")
        
        # Führen Sie die Suche für jedes Muster aus und speichern Sie die Ergebnisse
        jpg_files = glob.glob(jpg_pattern, recursive=True)
        jpeg_files = glob.glob(jpeg_pattern, recursive=True)
        png_files = glob.glob(png_pattern, recursive=True)

        # Vereinigen Sie die Listen
        all_image_files = jpg_files + jpeg_files + png_files

        filtered_files = [f for f in all_image_files if "_passend" in os.path.basename(f)]
        
        return filtered_files

class MusicApp(App):
    def build(self):
        return AlbumView()

if __name__ == '__main__':
    MusicApp().run()