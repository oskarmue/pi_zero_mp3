'''
Probleme die ich bei den animationen nicht zu lösen weiß:
-oberes/ unteres widget nicht über den gesamten Bildschirm "fliegen" lassen
-z layer hirarchien
potentielle Lösung
-die widgets nicht wirklcih bewegen
    -widget auf die nächste position animieren
    -dann in einem schritt: auf position zurück setzen und bilder tauschen
    -> die widget wechseln zwischen zwei positionen und wechseln bilder -> gleich bleibende hierarchien und widgets "fliegen" nicht
'''
import glob
import os
import math
from collections import deque

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Mesh, Translate, PushMatrix, PopMatrix
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty
import psutil

Window.borderless = True
import time


class AccuratePerspective(Widget):
    angle = NumericProperty(0)
    distance = NumericProperty(100)
    richtung = StringProperty('neutral')

    def __init__(self, image_path, **kwargs):
        super().__init__(**kwargs)

        self.standard_side_length = 200
        self.default_distance = 100

        self.vertices_1 = [
            0, 0, 0, 0,
            self.standard_side_length, 0, 1, 0,
            0, self.standard_side_length, 0, 1,
            self.standard_side_length, self.standard_side_length, 1, 1
        ]

        with self.canvas:
            PushMatrix()
            self.pos_transformation = Translate(self.x, self.y)
            self.mesh = Mesh(
                vertices=self.vertices_1,
                indices=[0, 1, 2, 3],
                mode='triangle_strip',
                texture=CoreImage(image_path).texture
            )
            PopMatrix()

        self.bind(pos=self._update_translate)
        self.bind(angle=self._update_mesh)
        self.bind(distance=self._update_mesh)
        self.bind(richtung=self._update_mesh)

    def _update_translate(self, *args):
        self.pos_transformation.x = self.x
        self.pos_transformation.y = self.y

    def _update_mesh(self, *args):
        new_angle = math.radians(self.angle)
        new_distance = self.distance

        scale = self.default_distance / new_distance
        half_diff = (self.standard_side_length -
                     (self.standard_side_length * self.default_distance) / new_distance) / 2

        delta_h = self.standard_side_length * (1 - math.cos(new_angle)) * scale

        if self.richtung == 'vor':
            ol = (half_diff, self.standard_side_length - half_diff)
            or_ = (self.standard_side_length - half_diff, self.standard_side_length - half_diff)
            ul = (half_diff + delta_h, half_diff + delta_h)
            ur = (self.standard_side_length - half_diff - delta_h, half_diff + delta_h)

        elif self.richtung == 'zurueck':
            ul = (half_diff, half_diff)
            ur = (self.standard_side_length - half_diff, half_diff)
            ol = (half_diff + delta_h, self.standard_side_length - half_diff - delta_h)
            or_ = (self.standard_side_length - half_diff - delta_h,
                   self.standard_side_length - half_diff - delta_h)

        else:
            ul = (half_diff, half_diff)
            ur = (self.standard_side_length - half_diff, half_diff)
            ol = (half_diff, self.standard_side_length - half_diff)
            or_ = (self.standard_side_length - half_diff, self.standard_side_length - half_diff)

        self.mesh.vertices = [
            ol[0], ol[1], 0, 0,
            or_[0], or_[1], 1, 0,
            ul[0], ul[1], 0, 1,
            ur[0], ur[1], 1, 1
        ]

    def change_texture(self, image_path):
        self.mesh.texture = CoreImage(image_path).texture

    def animate_to(self, pos, richtung, angle, distance, duration=0.25):
        Animation.cancel_all(self)
        
        self.richtung = richtung
        Animation(
            x=pos[0],
            y=pos[1],
            angle=angle,
            distance=distance,
            duration=duration,
            t='out_cubic'
        ).start(self)


class MyApp(App):
    def build(self):
        self.proc = psutil.Process(os.getpid())

        self.distance_background = 120
        self.distance_foregorund = 100
        self.angle_background = 40
        self.angle_foreground = 0

        self.positionen = [
            [100, 950, 0], [100, 800, 0], [100, 650, 0], [100, 500, 0],
            [100, 350, 1],
            [100, 200, 2], [100, 50, 2], [100, -100, 2], [100, -250, 2]
        ]
        self.num_widgets = len(self.positionen)

        self.image_paths = self.find_images("Music_Library")
        self.widgets = deque(maxlen=len(self.positionen))
        self.index = 0

        self.layout = FloatLayout()

        for i, p in enumerate(self.positionen):
            w = AccuratePerspective(self.image_paths[i])
            w.pos = (p[0], p[1])
            self.widgets.append(w)
            self.layout.add_widget(w)

        btns = BoxLayout(size_hint_y=0.1)
        up = Button(text="up")
        down = Button(text="down")
        up.bind(on_press=lambda x: self.flow_up())
        down.bind(on_press=lambda x: self.flow_down())
        btns.add_widget(up)
        btns.add_widget(down)

        self.layout.add_widget(btns)
        self._apply_layout()
        return self.layout

    def _apply_layout(self):
        for i, w in enumerate(self.widgets):
            x, y, mode = self.positionen[i]
            if mode == 0:
                r, a, d = 'vor', self.angle_background, self.distance_background
            elif mode == 2:
                r, a, d = 'zurueck', self.angle_background, self.distance_background
            else:
                r, a, d = 'neutral', self.angle_foreground, self.distance_foregorund

            w.animate_to((x, y), r, a, d)


    def flow_down(self):
        if self.index + len(self.widgets) >= len(self.image_paths):
            return

        self.widgets[0].change_texture(self.image_paths[self.index + len(self.widgets)])

        self.index += 1
        self.widgets.append(self.widgets.popleft())
        self._apply_layout()

    def flow_up(self):
        self.proc.cpu_percent(interval=None)
        start_cpu = time.process_time()
        start_real = time.perf_counter()
        if self.index == 0:
            return
        self.index -= 1

        self.widgets[-1].change_texture(self.image_paths[self.index])

        self.widgets.appendleft(self.widgets.pop())
        self._apply_layout()
        auslastung = self.proc.cpu_percent(interval=None)
        ende_cpu = time.process_time()
        ende_real = time.perf_counter()

        cpu_zeit = ende_cpu - start_cpu
        echt_zeit = ende_real - start_real
        print(f"CPU-Auslastung während der Funktion: {auslastung}%")
        auslastung_anteil = (cpu_zeit / echt_zeit) * 100
        print(f"Die CPU war zu {auslastung_anteil:.1f}% der {cpu_zeit} sec aktiv beschäftigt.")
    
    def find_images(self, directory):
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


if __name__ == "__main__":
    MyApp().run()
