
#scp -r /home/om/Desktop/Cover_Flow_test pi@192.168.2.126:/home/pi/
#scp /home/om/Desktop/Cover_Flow_test/cover_flow_test_deque_eigene_animaion.py pi@192.168.2.126:/home/pi/Cover_Flow_test/
#where to get album cover art in high quality: https://covers.musichoarders.xyz/
#Recycle view kann das was ich ungefähr möchte - viele bilder laden ein paar widgets vorbehalten und dann die bilder in den widgets austauschen -> bilder werden einmal geladen und es müssen nur eine handvoll
#widgets initiiert werden
#Imports


'''
die datein davor und danach selber einlesen und der image paths liste vorne und hinten anhängen

'''
import glob
import os
import math
from collections import deque
import random

from kivy.config import Config

##Settings - config muss zuerst gesetzt werden
#Config.set('graphics', 'width', '240')
#Config.set('graphics', 'height', '320')
#Config.set('graphics', 'resizable', False) # Optional: Verhindert das Skalieren
'''
#Raspi Einstellungen
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['SDL_VIDEODRIVER'] = 'kmsdrm' # Nutzt den DRM/KMS Treiber für die GPU

Config.set('graphics', 'width', '240')
Config.set('graphics', 'height', '320')
#Config.set('graphics', 'fullscreen', '1')
Config.set('graphics', 'show_cursor', '0')
Config.set('graphics', 'multisamples', '0') # Wichtig für Performance auf SPI
'''


Config.set('graphics', 'width', '240')
Config.set('graphics', 'height', '320')
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

#auf 15 fps verringern
#Clock.max_iteration = 15

import psutil
import time

"""
standart cover größe definieren -> können vertices für die winkel berechnet werden
distanzen für die unterschiedlichen Positionen definieren
Positionene definieren
winkel für die Positionen definieren
"""

 
'''
indices der vertices, während mit einem vertices die lage einer dieser punkte beschrieben wird
[x, y, u, v]
x, y die koordinate im widget
u, v die stelle im importierten bild, wobei das 0 bis 1 ist
6 ---- 7 ---- 8
|      |      |
|      |      |
3 ---- 4 ---- 5
|      |      |
|      |      |
0 ---- 1 ---- 2
'''
class AccuratePerspective(Widget):
    def __init__(self, image_path, resolution, widget_breite, **kwargs):
        super().__init__(**kwargs)
        ########Widerverwendete Variablen                  damit so wenig variablen neu definiert werden müssen wie möglich, definiere ich hier einige, die dann den Funktionen übergeben werden
        self.standard_side_length = widget_breite #in pixel -> ein programm schreiben, welches alle bilder öffent und dann auf eine Pixelgröße hoch bzw. runter skaliert. Diese dann unter anderem Namen abspeichern, oder unter anderem Ordner, in dem dann gesucht wird
        self.standard_half = round(self.standard_side_length/2)

        self.resolution = resolution

        self.indices_1, self.vertices_1, self.v_, v__= self.foward_lean(100, 100, 0, self.standard_side_length, self.resolution)
        self.default_distance = 100
        self.new_sidelength_diff_by_half = 0 #muss später wenn man die richtigen settings gefunden hat eigentliche auch nicht immer aufs neue berechnet werden

        self.image_path = image_path

        with self.canvas:
            PushMatrix()  # Aktuellen Zustand speichern

            self.pos_transformation = Translate(100, 100)

            # Start-Koordinaten (Trapez 1)
            self.mesh = Mesh(
                vertices =      self.vertices_1,
                indices =       self.indices_1,
                mode =          'triangles',
                texture =       CoreImage(image_path).texture
            )

            PopMatrix()

    def change_position(self, new_x, new_y):
        """Verschiebt das gesamte Mesh an eine neue Koordinate."""
        self.pos_transformation.x = new_x
        self.pos_transformation.y = new_y

    def vertices_an_distance_anpassen(self, resolution, widgetbreite, default_distance, new_distance, vertices):
        #Variablen
        step_in_percent = 1/resolution
        step_in_pixel = 1/resolution * widgetbreite #bildbreite = 200
        widgetbreite_halbiert = round(widgetbreite/2)

        #standart vertices und indices
        # --- Ursprüngliche Vertices ---
        '''
        vertices = []
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                vertices += [
                    round(j * step_in_pixel),
                    round(i * step_in_pixel),
                    round(j * step_in_percent, 2),
                    round(i * step_in_percent, 2)
                ]
        '''
        # --- Indices ---
        indices = []
        for i in range(resolution):
            for j in range(resolution):
                bl = i * (resolution + 1) + j
                br = bl + 1
                tl = bl + (resolution + 1)
                tr = tl + 1
                indices += [bl, br, tr, bl, tr, tl]
        
        #1. erstmal die entfernung in die variablen einarbeiten
        vertices_nach_wechsel = vertices[:]
        new_sidelength_diff_by_half = round((widgetbreite - (widgetbreite * default_distance)/new_distance)/2) # an den au0enpunkten = max_diff
        for i in range(0, len(vertices), 4):
            x = vertices[i]
            y = vertices[i+1]
            u = vertices[i+2]
            v = vertices[i+3]

            if x <= widgetbreite_halbiert:
                vertices_nach_wechsel[i]         = round(x + new_sidelength_diff_by_half * (widgetbreite_halbiert - x)/widgetbreite_halbiert)
                if y <= widgetbreite_halbiert:
                    vertices_nach_wechsel[i+1]   = round(y + new_sidelength_diff_by_half * (widgetbreite_halbiert - y)/widgetbreite_halbiert)
                else:
                    vertices_nach_wechsel[i+1]   = round(y - new_sidelength_diff_by_half *  (y - widgetbreite_halbiert)/widgetbreite_halbiert)

            else:
                vertices_nach_wechsel[i]         = round(x - new_sidelength_diff_by_half * (x -widgetbreite_halbiert)/widgetbreite_halbiert)
                if y <= widgetbreite_halbiert:
                    vertices_nach_wechsel[i+1]   = round(y + new_sidelength_diff_by_half * (widgetbreite_halbiert - y)/widgetbreite_halbiert)
                else:
                    vertices_nach_wechsel[i+1]   = round(y - new_sidelength_diff_by_half *  (y - widgetbreite_halbiert)/widgetbreite_halbiert)



        return indices, vertices, vertices_nach_wechsel, new_sidelength_diff_by_half

    def forward_punkte_berechnen_(self, resolution, widgetbreite, db_halbe, dh):

        step_in_percent = 1 / resolution
        step_in_pixel = widgetbreite / resolution
        widgetbreite_halbiert = widgetbreite / 2

        # --- Ursprüngliche Vertices ---
        vertices = []
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                vertices += [
                    round(j * step_in_pixel),
                    round(i * step_in_pixel),
                    round(j * step_in_percent, 2),
                    round(1 - i * step_in_percent, 2)
                ]
        
        # --- Indices ---
        indices = []
        for i in range(resolution):
            for j in range(resolution):
                bl = i * (resolution + 1) + j
                br = bl + 1
                tl = bl + (resolution + 1)
                tr = tl + 1
                indices += [bl, br, tr, bl, tr, tl]

        # --- obere & untere Punkte extrahieren ---
        nur_x_y = []
        for i in range(0, len(vertices), 4):
            nur_x_y.append(vertices[i])
            nur_x_y.append(vertices[i + 1])

        obere_punkte = nur_x_y[-(resolution + 1) * 2:]     # bleiben gleich
        untere_punkte = nur_x_y[:(resolution + 1) * 2]     # werden verändert

        # --- 1. Untere Punkte vertikal nach oben ziehen ---
        untere_punkte[1::2] = [y + dh for y in untere_punkte[1::2]]

        # --- 2. Horizontale Stauchung der unteren Punkte ---
        stauchungsfaktor = db_halbe / widgetbreite_halbiert

        for i in range(0, len(untere_punkte), 2):
            x = untere_punkte[i]
            if x < widgetbreite_halbiert:
                verschiebung = stauchungsfaktor * (widgetbreite_halbiert - x)
                untere_punkte[i] = x - verschiebung
            else:
                verschiebung = stauchungsfaktor * (x - widgetbreite_halbiert)
                untere_punkte[i] = x - verschiebung

        # --- 3. Winkel von oben nach unten ---
        winkel = []
        for i in range(0, (resolution + 1) * 2, 2):
            dx = untere_punkte[i] - obere_punkte[i]
            dy = untere_punkte[i + 1] - obere_punkte[i + 1]
            winkel.append(math.atan(dx / dy))

        # --- 4. Neue Vertices berechnen ---
        vertices_nach_wechsel = []

        for i in range(resolution + 1):
            y_verh = i * step_in_percent
            y_koor = i * step_in_pixel

            # vertikale Bewegung nimmt nach unten zu
            y_koor += dh * (1 - y_verh)

            for j in range(resolution + 1):
                x_koor = j * step_in_pixel
                x_verh = j * step_in_percent

                # horizontale Stauchung nimmt nach unten zu
                verschiebung = math.tan(winkel[j]) * (1 - y_verh) * step_in_pixel * resolution

                if x_koor < widgetbreite_halbiert:
                    x_koor += verschiebung
                else:
                    x_koor -= verschiebung

                vertices_nach_wechsel += [
                    round(x_koor),
                    round(y_koor),
                    round(x_verh, 2),
                    round(1 - y_verh, 2)
                ]

        return indices, vertices, vertices_nach_wechsel

    def backward_punkte_berechnen_(self, resolution, widgetbreite, db_halbe, dh):
        #resolution = 16
        step_in_percent = 1/resolution
        step_in_pixel = 1/resolution * widgetbreite #bildbreite = 200
        widgetbreite_halbiert = round(widgetbreite/2)

        # Vertices
        vertices = []
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                vertices += [
                    round(j * step_in_pixel),
                    round(i * step_in_pixel),
                    round(j * step_in_percent, 2),
                    round(1 - i * step_in_percent, 2)
                ]
        # Indices
        indices = []
        for i in range(resolution):
            for j in range(resolution):
                bl = i*(resolution+1) + j
                br = bl + 1
                tl = bl + (resolution+1)
                tr = tl + 1
                indices += [bl, br, tr, bl, tr, tl]

        #calculating the vertices after the perspective change

        #1. verschiebung der Punkte in der obersten reihe berechnen

        #2. Winkel der vertikalen berechnen

        #3. Die Zeilen entlang die punte neu berechnen
            #3.1 horizontale stauchung mittels winkel tan(winkel) * 

            #3.2 vertikale stauchung gleichmäßig -> gesamtstauchung/anzahl punkte = dh

        #NACH VORNE KIPPEN -> OBEREN PUNKTE VERÄNDERN
        #winkel_berechnen



        nur_x_y_vor = []
        for i in range(0, len(vertices), 4):
            if i + 1 < len(vertices):
                nur_x_y_vor.append(vertices[i])
                nur_x_y_vor.append(vertices[i+1])


        obere_punkte = nur_x_y_vor[-1*(resolution+1)*2:]
        untere_punkte = nur_x_y_vor[:(resolution+1)*2]


        #1. verschiebung der Punkte in der obersten Reihe berechnen
        #reduktion der y werte
        obere_punkte[1::2] = [x - dh for x in obere_punkte[1::2]]
        #reduktion der x werte
        stauchungsfaktor = db_halbe/widgetbreite_halbiert
        for i in range(len(obere_punkte)):
            if i%2 == 0: #das sind die x werte
                if obere_punkte[i] < widgetbreite_halbiert:#dann sind wir links der mitte und die verschiebung wird auf den Punkt addiert
                    verschiebung = stauchungsfaktor * (widgetbreite_halbiert - obere_punkte[i])
                    obere_punkte[i] = obere_punkte[i] + verschiebung
                else: #wir sind rechts der mitte und die Verschiebung wird von dem Punkt subtrahiert
                    verschiebung = stauchungsfaktor * (obere_punkte[i]-widgetbreite_halbiert)
                    obere_punkte[i] = obere_punkte[i] - verschiebung
                
        #2. winkel der vertikalen berechnen
        winkel = []
        for i in range(0, (resolution+1)*2, 2):
            dx = obere_punkte[i] - untere_punkte[i]
            dy = untere_punkte[i+1] - obere_punkte[i+1]
            winkel.append(math.atan(dx/dy)) #in radians - positiv mit der rechten daumen regel

        #3. Die Zeilen entlang die punte neu berechnen
            #3.1 horizontale stauchung mittels winkel tan(winkel) * 

            #3.2 vertikale stauchung gleichmäßig -> gesamtstauchung/anzahl zeilen = dh
        vertices_nach_wechsel = []

        for i in range(resolution+1): #vertikal - da wir untere und obere reihe schon haben, können wir diese einfach einfügen
            for j in range(resolution + 1):

                    x_koor = round(j*step_in_pixel)
                    y_koor = round(i*step_in_pixel)
                    x_verh = round(j*step_in_percent, 2)
                    y_verh = round(i*step_in_percent, 2)

                    y_koor = y_koor - round(dh * y_verh, 2)

                    if x_koor < widgetbreite_halbiert:#dann sind wir links der mitte und die verschiebung wird auf den Punkt addiert
                        verschiebung = math.tan(winkel[j]) * y_koor 
                        x_koor = x_koor - verschiebung
                    else: #wir sind rechts der mitte und die Verschiebung wird von dem Punkt subtrahiert
                        verschiebung = math.tan(winkel[j]) * y_koor 
                        x_koor = x_koor - verschiebung

                    vertices_nach_wechsel += [
                        x_koor,
                        y_koor,
                        x_verh, #bleibt gleich
                        1 - y_verh  #bleibt gleich
                    ]

        #vertices_nach_wechsel = vertices_nach_wechsel + vertices[-(resolution+1)*4:]


        return indices, vertices, vertices_nach_wechsel

    def calc_dh(self, default_distance, distance, angle_in_dec, widget_seitenlänge):
        entfernungs_skalier_faktor = distance/default_distance
        new_angle = math.radians(angle_in_dec)

        delta_h = widget_seitenlänge*(1-math.cos(new_angle)) * entfernungs_skalier_faktor

        return round(delta_h * entfernungs_skalier_faktor)

    def foward_lean(self, default_distance, distance, angle_in_dec, widget_seitenlänge, resolution):
        dh = self.calc_dh(default_distance, distance, angle_in_dec, widget_seitenlänge)

        indices, vertices_normal, vertices_gekippt = self.forward_punkte_berechnen_(resolution, widget_seitenlänge, dh/2, dh)
        
        indices, vertices_gekippt, vertices_gekippt_und_distant, new_sidelength_diff_by_half = self.vertices_an_distance_anpassen(resolution, widget_seitenlänge, default_distance, distance, vertices_gekippt)

        return indices, vertices_normal, vertices_gekippt, vertices_gekippt_und_distant

    def backward_lean(self, default_distance, distance, angle_in_dec, widget_seitenlänge, resolution):
        dh = self.calc_dh(default_distance, distance, angle_in_dec, widget_seitenlänge)

        indices, vertices_normal, vertices_gekippt = self.backward_punkte_berechnen_(resolution, widget_seitenlänge, dh, dh)
        
        indices, vertices_gekippt, vertices_gekippt_und_distant, new_sidelength_diff_by_half = self.vertices_an_distance_anpassen(resolution, widget_seitenlänge, default_distance, distance, vertices_gekippt)

        return indices, vertices_normal, vertices_gekippt, vertices_gekippt_und_distant

    def change_perspective(self, new_vertices):
 
        self.mesh.vertices = new_vertices

    def change_texture(self, image_path):
        self.mesh.texture = CoreImage(image_path).texture
        self.image_path = image_path

class MyApp(App):
    def build(self):
        self.proc = psutil.Process(os.getpid())
        #Parameters & fixed Variables
        self.distance_background    = 120
        self.distance_inbetween     = 110
        self.distance_foregorund    = 90
        self.angle_background       = 40
        self.angle_foreground       = 0
        self.positionen_in_reihenfolge = [
                                            [60, -60,   30, self.distance_background, 0], 
                                            [60, -30,   30, self.distance_background, 0],
                                            [60, 0,     30, self.distance_background, 0], #0 = backwards lean
                                            [60, 30,    30, self.distance_background, 0],
                                            [60, 60,    20, self.distance_inbetween, 0],
                                            [60, 108,   0, self.distance_foregorund, 0],
                                            [60, 160,   20, self.distance_inbetween, 1], #1 = forward lean
                                            [60, 190,   30, self.distance_background, 1],
                                            [60, 210,   30, self.distance_background, 1],
                                            [60, 240,   30, self.distance_background, 1],
                                            [60, 270,   30, self.distance_background, 1]
                                        ] #[pos_x, pos_y, angle, distance] - sonderfälle bei den enden, da zweimal das gleiche, da einer daobn nicht benötigt wird

        self.index_of_upper_cover   = 0
        self.image_paths = self.find_image_files_multiple_globs('Music_Library')
        print(self.image_paths)
        self.num_covers = len(self.image_paths)
        self.num_widgets = len(self.positionen_in_reihenfolge)
        self.widgets = deque(maxlen=self.num_widgets) #append/ appendleft - in dieser werden die textures zwischen gebuffert, sodass diese beim wechsel nicht immer neu geladen werden müssen

        self.dauer_animation_in_sec  = 0.5
        self.frames_per_sec          = 15
        self.frames_per_animation    = round(self.frames_per_sec * self.dauer_animation_in_sec)
        self.Zwischenpositionen      = [] #für jedes frame ein unterarray - das kann auch einma am Anfang des Programms berechnet werden -> bleibt dann gleich

        self.resolution_ = 10

        self.widget_breite = 120

        #Haupt-Layout erstellen
        self.layout = FloatLayout()

        Window.bind(on_key_down=self.on_key_down)

        self.vertices_animationen_runter    = []
        self.vertices_animationen_hoch      = deque(maxlen=self.num_widgets)

        #Die start widgets an den positionen erstellen und erste Bilder zuordnen - die positionen müssen in der reihenfolge liegen, wie die widgets sich überlappen sollen
        for i in range(self.index_of_upper_cover, len(self.positionen_in_reihenfolge)):
            #widget erstellen und der liste anhängen
            self.widgets.append(AccuratePerspective(image_path = self.image_paths[i], resolution=self.resolution_, widget_breite=self.widget_breite))
            x, y, angle, distance, lean = self.positionen_in_reihenfolge[i][:]
            self.widgets[i].change_position(new_x=x, new_y=y)

            if lean == 1:
                i_, v_1, v_2, v_3 = self.widgets[i].foward_lean(self.distance_foregorund, distance, angle, self.widget_breite, self.resolution_)
                
            else:
                i_, v_1, v_2, v_3 = self.widgets[i].backward_lean(self.distance_foregorund, distance, -1*angle, self.widget_breite, self.resolution_)
                
            self.widgets[i].change_perspective(v_3)
            self.layout.add_widget(self.widgets[i])

        #vertices für die animationen berechnen
        #runter: 1-> 2, 2-> 3, ..., ende -> 1
        for i in range(len(self.positionen_in_reihenfolge)):
            
            perspektiven = []

            if i == len(self.positionen_in_reihenfolge)-1: #das letzte widget muss nach oben
                x_1, y_1, angle_1, distance_1, lean_1 = self.positionen_in_reihenfolge[i][:]
                x_2, y_2, angle_2, distance_2, lean_2 = self.positionen_in_reihenfolge[0][:]

                idices, vertices_1, vertices_2, vertices_3 = self.widgets[0].backward_lean(100, distance_2, angle_2, self.widget_breite, self.resolution_)
                for s in range(self.frames_per_animation):
                    perspektiven.append([
                        x_2,
                        y_2,
                        vertices_3
                    ])

            else:
                x_1, y_1, angle_1, distance_1, lean_1 = self.positionen_in_reihenfolge[i][:]
                x_2, y_2, angle_2, distance_2, lean_2 = self.positionen_in_reihenfolge[i+1][:]

                d_x_per_frame           = (x_2 - x_1)/self.frames_per_animation
                d_y_per_frame           = (y_2 - y_1)/self.frames_per_animation
                d_distance_per_frame    = (distance_2 - distance_1)/self.frames_per_animation
                d_angle_per_frame       = (angle_2 - angle_1)/self.frames_per_animation

                for s in range(self.frames_per_animation):
                    angle_s = angle_1 + s*d_angle_per_frame
                    distance_s = distance_1 + s * d_distance_per_frame
                    if lean_2 == 1:
                        idices, vertices_1, vertices_2, vertices_3 = self.widgets[0].foward_lean(100, distance_s, angle_s, self.widget_breite, self.resolution_)
                    else:
                        idices, vertices_1, vertices_2, vertices_3 = self.widgets[0].backward_lean(100, distance_s, angle_s, self.widget_breite, self.resolution_)

                    
                    perspektiven.append([
                                        x_1 + s * d_x_per_frame, 
                                        y_1 + s * d_y_per_frame, 
                                        vertices_3
                                        ])
            
            self.vertices_animationen_runter.append(perspektiven)

        #hoch: 1-> ende, 2 -> 1, ....
        for i in range(len(self.positionen_in_reihenfolge)):
            perspektiven = []

            if i == 0:
                x_1, y_1, angle_1, distance_1, lean_1 = self.positionen_in_reihenfolge[0][:]
                x_2, y_2, angle_2, distance_2, lean_2 = self.positionen_in_reihenfolge[-1][:]

                idices, vertices_1, vertices_2, vertices_3 = self.widgets[0].backward_lean(100, distance_2, angle_2, self.widget_breite, self.resolution_)
                for s in range(self.frames_per_animation):
                    perspektiven.append([
                        x_2,
                        y_2,
                        vertices_3
                    ])

            else:
                x_1, y_1, angle_1, distance_1, lean_1 = self.positionen_in_reihenfolge[i][:]
                x_2, y_2, angle_2, distance_2, lean_2 = self.positionen_in_reihenfolge[i-1][:]

                d_x_per_frame           = (x_2 - x_1)/self.frames_per_animation
                d_y_per_frame           = (y_2 - y_1)/self.frames_per_animation
                d_distance_per_frame    = (distance_2 - distance_1)/self.frames_per_animation
                d_angle_per_frame       = (angle_2 - angle_1)/self.frames_per_animation

                for s in range(self.frames_per_animation):
                    angle_s = angle_1 + s*d_angle_per_frame
                    distance_s = distance_1 + s * d_distance_per_frame

                    if lean_2 == 1:
                        idices, vertices_1, vertices_2, vertices_3 = self.widgets[0].foward_lean(100, distance_s, angle_s, self.widget_breite, self.resolution_)
                    else:
                        idices, vertices_1, vertices_2, vertices_3 = self.widgets[0].backward_lean(100, distance_s, angle_s, self.widget_breite, self.resolution_)
                    
                    perspektiven.append([
                                        x_1 + s * d_x_per_frame, 
                                        y_1 + s * d_y_per_frame, 
                                        vertices_3
                                        ])

            self.vertices_animationen_hoch.append(perspektiven)

        self.layout.remove_widget(self.widgets[5])
        self.layout.remove_widget(self.widgets[6])
        self.layout.remove_widget(self.widgets[7])
        self.layout.remove_widget(self.widgets[8])

        self.layout.add_widget(self.widgets[8], index=0)
        self.layout.add_widget(self.widgets[7], index=0)
        self.layout.add_widget(self.widgets[6], index=0)
        self.layout.add_widget(self.widgets[5], index=0)

        self.vertices_animationen_hoch.append(self.vertices_animationen_hoch[0])
        self.vertices_animationen_hoch.append(self.vertices_animationen_hoch[0])
        
        return self.layout

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 273:  # Pfeil nach oben
            self.cover_flow_up()

        elif key == 274:  # Pfeil nach unten
            self.cover_flow_down()
    
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

        random.shuffle(filtered_files)
        
        return filtered_files

    def cover_flow_down(self):

        if self.index_of_upper_cover == len(self.image_paths)-len(self.widgets): #das hier muss noch so angepasst werden, sodass die menge an widgets angepasst werden kann
            #die letzten zwei "buffer cove" müssen noch hoch geholt werden
            #hier müsste es dann für paar steps weiter gehen ohne, dass neue alben hinterhergeschoben werden
            return
        else:
            #self.widgets[-1].change_texture(self.image_paths[self.index_of_upper_cover + 10])
            self.index_of_upper_cover += 1

            #6. animation beginnen
            self.current_frame = 0

            self.animation_event = Clock.schedule_interval(self.animate_step_zurueck, self.dauer_animation_in_sec/self.frames_per_animation)
            print(self.widgets[3].image_path)

            self.widgets.appendleft(self.widgets[-1])
            self.widgets[0].change_texture(self.image_paths[self.index_of_upper_cover + len(self.widgets)-1])

    def cover_flow_up(self):
        if self.index_of_upper_cover == 0:
            #die letzten zwei "buffer cove" müssen noch hoch geholt werden
            #hier müsste es dann für paar steps weiter gehen ohne, dass neue alben hinterhergeschoben werden
            return
        else:
            self.index_of_upper_cover -= 1
            #6. animation beginnen
            self.current_frame = 0

            self.animation_event = Clock.schedule_interval(self.animate_step_vor, self.dauer_animation_in_sec/self.frames_per_animation)
            print(self.widgets[5].image_path)

            #widet von oben nach unten packen & dessen texture verändern
            self.widgets.append(self.widgets[0]) #dran denken, das untere widet hat das kleinste y und ist die 0
            self.widgets[-1].change_texture(self.image_paths[self.index_of_upper_cover])
            
    def animate_step_zurueck(self, dt):
        # Prüfen, ob Animation zu Ende ist
        if self.current_frame >= self.frames_per_animation:
            Clock.unschedule(self.animation_event)
            return False #dann hört die Clock auf

        for widget_nr in range(len(self.positionen_in_reihenfolge)):
            pos__persp_data = self.vertices_animationen_runter[widget_nr][self.current_frame]
            # [x, y, angle, distance]
            self.widgets[widget_nr].change_position(new_x=pos__persp_data[0], new_y=pos__persp_data[1])
            self.widgets[widget_nr].change_perspective(pos__persp_data[2])

        
        self.reorganze_widgets()

        self.current_frame += 1

    def animate_step_vor(self, dt):
        # Prüfen, ob Animation zu Ende ist
        if self.current_frame >= self.frames_per_animation:
            Clock.unschedule(self.animation_event)
            return False #dann hört die Clock auf

        for widget_nr in range(len(self.positionen_in_reihenfolge)):
            pos__persp_data = self.vertices_animationen_hoch[widget_nr][self.current_frame]
            # [x, y, angle, distance]
            self.widgets[widget_nr].change_position(new_x=pos__persp_data[0], new_y=pos__persp_data[1])
            self.widgets[widget_nr].change_perspective(pos__persp_data[2])




        self.reorganze_widgets()

        self.current_frame += 1
    
    def reorganze_widgets(self):
        self.layout.remove_widget(self.widgets[1])
        self.layout.remove_widget(self.widgets[2])
        self.layout.remove_widget(self.widgets[3])
        self.layout.remove_widget(self.widgets[4])
        
        self.layout.remove_widget(self.widgets[5])
        self.layout.remove_widget(self.widgets[6])
        self.layout.remove_widget(self.widgets[7])
        self.layout.remove_widget(self.widgets[8])
        self.layout.remove_widget(self.widgets[9])

        self.layout.add_widget(self.widgets[1])
        self.layout.add_widget(self.widgets[2])
        self.layout.add_widget(self.widgets[3])
        
        self.layout.add_widget(self.widgets[9])
        self.layout.add_widget(self.widgets[8])
        self.layout.add_widget(self.widgets[7])
        self.layout.add_widget(self.widgets[6])
        self.layout.add_widget(self.widgets[5])
        self.layout.add_widget(self.widgets[4])

if __name__ == '__main__':
    MyApp().run()