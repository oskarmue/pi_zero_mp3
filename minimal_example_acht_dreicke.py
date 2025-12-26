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
    def __init__(self, image_path, resolution, **kwargs):
        super().__init__(**kwargs)
        ########Widerverwendete Variablen                  damit so wenig variablen neu definiert werden müssen wie möglich, definiere ich hier einige, die dann den Funktionen übergeben werden
        self.standard_side_length = 200 #in pixel -> ein programm schreiben, welches alle bilder öffent und dann auf eine Pixelgröße hoch bzw. runter skaliert. Diese dann unter anderem Namen abspeichern, oder unter anderem Ordner, in dem dann gesucht wird
        self.standard_half = round(self.standard_side_length/2)

        self.resolution = resolution

        self.indices_1, self.vertices_1, self.v_, v__= self.foward_lean(100, 100, 0, self.standard_side_length, self.resolution)
        self.default_distance = 100
        self.new_sidelength_diff_by_half = 0 #muss später wenn man die richtigen settings gefunden hat eigentliche auch nicht immer aufs neue berechnet werden

        with self.canvas:
            PushMatrix()  # Aktuellen Zustand speichern

            self.pos_transformation = Translate(750, 750)

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
                    round(i * step_in_percent, 2)
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
                    round(y_verh, 2)
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
                    round(i * step_in_percent, 2)
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
                        y_verh  #bleibt gleich
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

class MyApp(App):
    def build(self):
        self.proc = psutil.Process(os.getpid())
        #Parameters & fixed Variables
        self.distance_background    = 120
        self.distance_foregorund    = 100
        self.angle_background       = 40
        self.angle_foreground       = 0
        self.positionen_in_reihenfolge    = [
                                       [100, 350, -30, self.distance_foregorund]
                                    ] #[pos_x, pos_y, angle, distance] - sonderfälle bei den enden, da zweimal das gleiche, da einer daobn nicht benötigt wird

        self.index_of_upper_cover   = 0
        self.image_paths = self.find_image_files_multiple_globs('Music_Library')
        self.num_covers = len(self.image_paths)
        self.num_widgets = len(self.positionen_in_reihenfolge)
        self.widgets = deque(maxlen=self.num_widgets) #append/ appendleft - in dieser werden die textures zwischen gebuffert, sodass diese beim wechsel nicht immer neu geladen werden müssen

        self.dauer_animation_in_sec  = 0.5
        self.frames_per_sec          = 60
        self.frames_per_animation    = round(self.frames_per_sec * self.dauer_animation_in_sec)
        self.Zwischenpositionen      = [] #für jedes frame ein unterarray - das kann auch einma am Anfang des Programms berechnet werden -> bleibt dann gleich

        self.resolution_ = 64


            

        #Haupt-Layout erstellen
        self.layout = FloatLayout()

        #Die start widgets an den positionen erstellen und erste Bilder zuordnen - die positionen müssen in der reihenfolge liegen, wie die widgets sich überlappen sollen
        for i in range(self.index_of_upper_cover, len(self.positionen_in_reihenfolge)):
            #widget erstellen und der liste anhängen
            self.widgets.append(AccuratePerspective(image_path = self.image_paths[i], resolution=self.resolution_))
            self.widgets[i].change_position(new_x=100, new_y=400)
            i_, v_1, v_2, v_3 = self.widgets[i].foward_lean(100, 100, 20, 200, self.resolution_)
            self.widgets[i].change_perspective(v_1)

            self.layout.add_widget(self.widgets[i])
        

        #Button zum testen hinzufügen
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)

        btn_1 = Button(text="vor")
        btn_1.bind(on_press=lambda x: self.cover_flow_up())

        btn_2 = Button(text="zurueck")
        btn_2.bind(on_press=lambda x: self.cover_flow_down())

        button_layout.add_widget(btn_1)
        button_layout.add_widget(btn_2)
        self.layout.add_widget(button_layout)

        self.perspectiven = []
        self.perspectiven_vor = []


        x_1, y_1, angle_1, distance_1 = 100, 350, 0, 100
        x_2, y_2, angle_2, distance_2 = 100, 350, 30, 100
        d_x_per_frame           = (x_2 - x_1)/self.frames_per_animation
        d_y_per_frame           = (y_2 - y_1)/self.frames_per_animation
        d_distance_per_frame    = (distance_2 - distance_1)/self.frames_per_animation
        d_angle_per_frame       = (angle_2 - angle_1)/self.frames_per_animation


        for s in range(self.frames_per_animation):
            angle_s = angle_1 + s*d_angle_per_frame
            idices, vertices_1, vertices_2, vertices_3 = self.widgets[0].foward_lean(100, 100, angle_s, 200, self.resolution_)
            self.perspectiven.append([
                                100, 
                                400, 
                                vertices_3
                                ])

        for s in range(self.frames_per_animation):
            angle_s = angle_2 - s*d_angle_per_frame
            idices, vertices_1, vertices_2, vertices_3 = self.widgets[0].foward_lean(100, 100, angle_s, 200, self.resolution_)
            self.perspectiven_vor.append([
                                100, 
                                400, 
                                vertices_3
                                ])

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

    def cover_flow_down(self):

        #6. animation beginnen
        self.current_frame = 0
        
        self.animation_event = Clock.schedule_interval(self.animate_step_zurueck, self.dauer_animation_in_sec/self.frames_per_animation)

    def cover_flow_up(self):

        #6. animation beginnen
        self.current_frame = 0
        
        self.animation_event = Clock.schedule_interval(self.animate_step_vor, self.dauer_animation_in_sec/self.frames_per_animation)


    def animate_step_zurueck(self, dt):
        # Prüfen, ob Animation zu Ende ist
        if self.current_frame >= self.frames_per_animation:
            Clock.unschedule(self.animation_event)
            return False #dann hört die Clock auf

        pos__persp_data = self.perspectiven[self.current_frame]
        # [x, y, angle, distance]
        self.widgets[0].change_position(new_x=pos__persp_data[0], new_y=pos__persp_data[1])
        self.widgets[0].change_perspective(pos__persp_data[2])

        self.current_frame += 1

    def animate_step_vor(self, dt):
        # Prüfen, ob Animation zu Ende ist
        if self.current_frame >= self.frames_per_animation:
            Clock.unschedule(self.animation_event)
            return False #dann hört die Clock auf

        pos__persp_data = self.perspectiven_vor[self.current_frame]
        # [x, y, angle, distance]
        self.widgets[0].change_position(new_x=pos__persp_data[0], new_y=pos__persp_data[1])
        self.widgets[0].change_perspective(pos__persp_data[2])

        self.current_frame += 1

if __name__ == '__main__':
    MyApp().run()