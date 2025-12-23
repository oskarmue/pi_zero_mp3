#where to get album cover art in high quality: https://covers.musichoarders.xyz/
#Recycle view kann das was ich ungefähr möchte - viele bilder laden ein paar widgets vorbehalten und dann die bilder in den widgets austauschen -> bilder werden einmal geladen und es müssen nur eine handvoll
#widgets initiiert werden
#Imports
import glob
import os
import math
from collections import deque

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
#from kivy.uix.image import Image


#from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
Window.borderless = True
#Window.size = (400, 900)

from kivy.graphics import RenderContext, Color, Rectangle, BindTexture
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage

from kivy.core.image import Image

from kivy.clock import Clock

import psutil
import time

"""
standart cover größe definieren -> können vertices für die winkel berechnet werden
distanzen für die unterschiedlichen Positionen definieren
Positionene definieren
winkel für die Positionen definieren
"""

 

class AccuratePerspective(Widget):
    def __init__(self, image_path, **kwargs):
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

            self.pos_transformation = Translate(750, 750)

            # Start-Koordinaten (Trapez 1)
            self.mesh = Mesh(
                vertices =      self.vertices_1,
                indices =       [0, 1, 2, 3],
                mode =          'triangle_strip',
                texture =       CoreImage(image_path).texture
            )

            PopMatrix()

    def change_position(self, new_x, new_y):
        """Verschiebt das gesamte Mesh an eine neue Koordinate."""
        self.pos_transformation.x = new_x
        self.pos_transformation.y = new_y

    def change_perspective(self, new_angle_deg = 0, new_distance = 100):

        new_angle = math.radians(new_angle_deg)

        #je nach dem, ob sich das widget ober oder unethalb des "Mittelbildes" befindet, bleiben die oberen oder unteren Ecken gleich
        self.entfernungs_skalierungsfaktor = self.default_distance/new_distance
        self.new_sidelength_diff_by_half = round((self.standard_side_length - (self.standard_side_length * self.default_distance)/new_distance)/2) # durch die enfernung

        self.delta_h = round(self.standard_side_length*(1-math.cos(new_angle)) * self.entfernungs_skalierungsfaktor)
        self.dist_durch_neigung = math.sin(new_angle) * self.standard_side_length
        self.delta_b = round(self.standard_side_length*0.5*(1-self.default_distance/(self.default_distance + self.dist_durch_neigung)))
        if new_angle >= 0:
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
        else:
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

        self.mesh.vertices = self.vertices_1

    def change_texture(self, image_path):
        self.mesh.texture = CoreImage(image_path).texture

class MyApp(App):
    def build(self):
        self.proc = psutil.Process(os.getpid())
        #Parameters & fixed Variables
        self.distance_background    = 120
        self.distance_foregorund    = 100
        self.angle_background       = 40
        self.angle_foreground       = 0
        self.positionen_in_reihenfolge    = [
                                        [100, 950, self.angle_background, self.distance_background], [100, 800, self.angle_background, self.distance_background], [100, 650, self.angle_background, self.distance_background], [100, 500, self.angle_background, self.distance_background],
                                        [100, 350, self.angle_foreground, self.distance_foregorund], 
                                        [100, 200, -1*self.angle_background, self.distance_background], [100, 50, -1*self.angle_background, self.distance_background], [100, -100, -1*self.angle_background, self.distance_background], [100, -250, -1*self.angle_background, self.distance_background],
                                        
                                    ] #[pos_x, pos_y, angle, distance] - sonderfälle bei den enden, da zweimal das gleiche, da einer daobn nicht benötigt wird


        self.index_of_upper_cover   = 0
        self.image_paths = self.find_image_files_multiple_globs('Music_Library')
        self.num_covers = len(self.image_paths)
        self.num_widgets = len(self.positionen_in_reihenfolge)
        self.widgets = deque(maxlen=self.num_widgets) #append/ appendleft - in dieser werden die textures zwischen gebuffert, sodass diese beim wechsel nicht immer neu geladen werden müssen



        self.dauer_animation_in_sec  = 1
        self.frames_per_sec          = 30
        self.frames_per_animation    = round(self.frames_per_sec * self.dauer_animation_in_sec)
        self.Zwischenpositionen      = [] #für jedes frame ein unterarray - das kann auch einma am Anfang des Programms berechnet werden -> bleibt dann gleich
        for i in range(len(self.positionen_in_reihenfolge)-1):
            #derzeitige position    = self.positionen_in_reihenfolge[i+1]
            #angestrebte position   = self.positionen_in_reihenfolge[i]
            x_1, y_1, angle_1, distance_1 = self.positionen_in_reihenfolge[i+1]
            x_2, y_2, angle_2, distance_2 = self.positionen_in_reihenfolge[i]
            d_x_per_frame           = (x_2 - x_1)/self.frames_per_animation
            d_y_per_frame           = (y_2 - y_1)/self.frames_per_animation
            d_distance_per_frame    = (distance_2 - distance_1)/self.frames_per_animation
            d_angle_per_frame       = (angle_2 - angle_1)/self.frames_per_animation

            positionen_i = []

            for s in range(self.frames_per_animation):
                positionen_i.append([
                                    x_1 + s*d_x_per_frame, 
                                    y_1 + s*d_y_per_frame, 
                                    angle_1 + s*d_angle_per_frame, 
                                    distance_1 + s*d_distance_per_frame
                                    ])
                
            self.Zwischenpositionen.append(positionen_i)

















        #Haupt-Layout erstellen
        self.layout = FloatLayout()

        #Die start widgets an den positionen erstellen und erste Bilder zuordnen - die positionen müssen in der reihenfolge liegen, wie die widgets sich überlappen sollen
        for i in range(self.index_of_upper_cover, len(self.positionen_in_reihenfolge)):
            #widget erstellen und der liste anhängen
            self.widgets.append(AccuratePerspective(image_path = self.image_paths[i]))
            self.widgets[i].change_position(new_x=self.positionen_in_reihenfolge[i][0], new_y=self.positionen_in_reihenfolge[i][1])

            self.widgets[i].change_perspective(new_angle_deg=self.positionen_in_reihenfolge[i][2], new_distance=self.positionen_in_reihenfolge[i][3])

            self.layout.add_widget(self.widgets[i])
        
        #Die lösung gefällt mir noch nicht gut, würde lieber direkt in der richtigen reihenfolge die wigets hinzufügen/ organisieren
        self.layout.remove_widget(self.widgets[4])
        self.layout.remove_widget(self.widgets[5])
        self.layout.remove_widget(self.widgets[6])

        self.layout.add_widget(self.widgets[6], index=0)
        self.layout.add_widget(self.widgets[5], index=0)
        self.layout.add_widget(self.widgets[4], index=0)


        #Button zum testen hinzufügen
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        btn_1 = Button(text="up")
        btn_1.bind(on_press=lambda x: self.cover_flow_up())

        btn_2 = Button(text="down")
        btn_2.bind(on_press=lambda x: self.cover_flow_down())

        button_layout.add_widget(btn_1)
        button_layout.add_widget(btn_2)
        self.layout.add_widget(button_layout)


        return self.layout
    
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

    def reorder_certain_widgets(self):
            #Die lösung gefällt mir noch nicht gut, würde lieber direkt in der richtigen reihenfolge die wigets hinzufügen/ organisieren
            self.layout.remove_widget(self.widgets[4])
            self.layout.remove_widget(self.widgets[5])
            self.layout.remove_widget(self.widgets[6])

            self.layout.add_widget(self.widgets[6], index=0)
            self.layout.add_widget(self.widgets[5], index=0)
            self.layout.add_widget(self.widgets[4], index=0)

    def cover_flow_down(self):
        #1. wenn das unterste Bild angezeigt wird, kann dieser button nicht ausgeführt werden - sonst einem widget ein neues Bild zuordnen
        if self.index_of_upper_cover+self.num_widgets == self.num_covers:
            #die letzten zwei "buffer coveers" müssen noch hoch geholt werden
            return
        
        #2. dem widget welches an das andere ende gestellt wird eine neue textur geben
        self.widgets[0].change_texture(self.image_paths[self.index_of_upper_cover+self.num_widgets])

        #3. das oberste cover ist nun nicht mehr das 0. aus der liste
        self.index_of_upper_cover += 1

        #4. die widgets bewegen sich eins nach unten -> und verändern ggf. Ihre perspektive
        self.widgets.append(self.widgets[0])

        #5. dem widget welches über den gesamten screen muss um ans andere ende zu kommen ohne amiation position ändern
        self.widgets[-1].change_position(
            new_x=self.positionen_in_reihenfolge[-1][0], 
            new_y=self.positionen_in_reihenfolge[-1][1])
        
        #6. animation beginnen
        self.current_frame = 0
        
        # Clock startet: Ruft '_animate_step' ca. 30-60 mal pro Sekunde auf
        # Wir speichern das Event in 'self.anim_event', um es später stoppen zu können
        self.animation_event = Clock.schedule_interval(self.animate_step, self.dauer_animation_in_sec/self.frames_per_animation)

    def animate_step(self, dt):
        # Prüfen, ob Animation zu Ende ist
        if self.current_frame >= self.frames_per_animation:
            Clock.unschedule(self.animation_event)
            return False #dann hört die Clock auf
        
        # 4. Die eigentliche Bewegung
        for i in range(len(self.positionen_in_reihenfolge) - 1):
            pos__persp_data = self.Zwischenpositionen[i][self.current_frame]
            # [x, y, angle, distance]
            self.widgets[i].change_position(new_x=pos__persp_data[0], new_y=pos__persp_data[1])
            self.widgets[i].change_perspective(new_angle_deg=pos__persp_data[2], new_distance=pos__persp_data[3])

        # 5. Z-Index / Sortierung korrigieren
        # (Das muss in jedem Frame passieren, damit die Überlappung stimmt)
        self.reorder_certain_widgets()

        # Frame-Zähler erhöhen
        self.current_frame += 1
    
    def cover_flow_down_(self): #-> die widgets bewegen sich hoch

        '''
        um das animiert zu bekommen
        1. nur die animieren, die zu sehen sind -> den rest "einfach" mit einem mal umsetzen
        2. Ziel Koordinaten für jedes widget ermitteln
        3. zwischenschritte der widgets in einer liste speichern
        4. durch Liste durchgehen und in jedem schritt jedes widget um einen Schritt weiter bewegen
        5. und dann in jedem schritt auch jedes widget wieder neu sortieren (die drei removen und hinzufügen)
        '''

        #1. wenn das unterste Bild angezeigt wird, kann dieser button nicht ausgeführt werden - sonst einem widget ein neues Bild zuordnen
        if self.index_of_upper_cover+self.num_widgets == self.num_covers:
            #die letzten zwei "buffer coveers" müssen noch hoch geholt werden
            return
        
        #2. dem widget welches an das andere ende gestellt wird eine neue textur geben
        self.widgets[0].change_texture(self.image_paths[self.index_of_upper_cover+self.num_widgets])

        #3. das oberste cover ist nun nicht mehr das 0. aus der liste
        self.index_of_upper_cover += 1

        #4. die widgets bewegen sich eins nach unten -> und verändern ggf. Ihre perspektive
        self.widgets.append(self.widgets[0])

        #5. dem widget welches über den gesamten screen muss um ans andere ende zu kommen ohne amiation position ändern
        self.widgets[-1].change_position(
            new_x=self.positionen_in_reihenfolge[-1][0], 
            new_y=self.positionen_in_reihenfolge[-1][1])

        #6. restlichen Widgets in einer Animation updaten
        for s in range(self.frames_per_animation):
            for i in range(len(self.positionen_in_reihenfolge)-1):
                self.widgets[i].change_position(
                    new_x=self.Zwischenpositionen[i][s][0], 
                    new_y=self.Zwischenpositionen[i][s][1])
                self.widgets[i].change_perspective(
                    new_angle_deg=self.Zwischenpositionen[i][s][2] , 
                    new_distance=self.Zwischenpositionen[i][s][3])

            self.reorder_certain_widgets()

                    

        '''
        for i in range(len(self.positionen_in_reihenfolge)-1):
            self.widgets[i].change_position(new_x=self.positionen_in_reihenfolge[i][0], new_y=self.positionen_in_reihenfolge[i][1])
            self.widgets[i].change_perspective(new_angle_deg=self.positionen_in_reihenfolge[i][2] , new_distance=self.positionen_in_reihenfolge[i][3])



    #Die lösung gefällt mir noch nicht gut, würde lieber direkt in der richtigen reihenfolge die wigets hinzufügen/ organisieren
        self.layout.remove_widget(self.widgets[4])
        self.layout.remove_widget(self.widgets[5])
        self.layout.remove_widget(self.widgets[6])

        self.layout.add_widget(self.widgets[6], index=0)
        self.layout.add_widget(self.widgets[5], index=0)
        self.layout.add_widget(self.widgets[4], index=0)
        '''

    def cover_flow_up(self):
        self.proc.cpu_percent(interval=None)
        start_cpu = time.process_time()
        start_real = time.perf_counter()
        #1. wenn das unterste Bild angezeigt wird, kann dieser button nicht ausgeführt werden
        if self.index_of_upper_cover == 0:
            #die letzten zwei "buffer cove" müssen noch hoch geholt werden
            return

        self.widgets[-1].change_texture(self.image_paths[self.index_of_upper_cover - 1])
        self.index_of_upper_cover -= 1

        #2. die widgets bewegen sich eins nach unten -> und verändern ggf. Ihre perspektive
        self.widgets.appendleft(self.widgets[-1])
            
        #self.widgets[i].change_perspective 
        for i in range(len(self.positionen_in_reihenfolge)):
            self.widgets[i].change_position(new_x=self.positionen_in_reihenfolge[i][0], new_y=self.positionen_in_reihenfolge[i][1])

            self.widgets[i].change_perspective(new_angle_deg=self.positionen_in_reihenfolge[i][2] , new_distance=self.positionen_in_reihenfolge[i][3])

        auslastung = self.proc.cpu_percent(interval=None)
        ende_cpu = time.process_time()
        ende_real = time.perf_counter()

        cpu_zeit = ende_cpu - start_cpu
        echt_zeit = ende_real - start_real
        print(f"CPU-Auslastung während der Funktion: {auslastung}%")
        auslastung_anteil = (cpu_zeit / echt_zeit) * 100
        print(f"Die CPU war zu {auslastung_anteil:.1f}% der {cpu_zeit} sec aktiv beschäftigt.")
    
    #Die lösung gefällt mir noch nicht gut, würde lieber direkt in der richtigen reihenfolge die wigets hinzufügen/ organisieren
        self.layout.remove_widget(self.widgets[4])
        self.layout.remove_widget(self.widgets[5])
        self.layout.remove_widget(self.widgets[6])

        self.layout.add_widget(self.widgets[6], index=0)
        self.layout.add_widget(self.widgets[5], index=0)
        self.layout.add_widget(self.widgets[4], index=0)

if __name__ == '__main__':
    MyApp().run()