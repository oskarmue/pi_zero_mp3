import os
import glob
import math
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.recycleview import RecycleView
from kivy.properties import StringProperty, NumericProperty
from kivy.graphics import Mesh, PushMatrix, PopMatrix, Translate
from kivy.core.image import Image as CoreImage
from kivy.cache import Cache
from kivy.lang import Builder

# Cache-Limit für den Pi Zero 2W
Cache.register('kv.image', limit=50)

# 1. Definiere das Widget-Design ZUERST
Builder.load_string('''
<AccuratePerspective>:
    # Wir definieren hier nur die Größe des "Containers"
    # Die Grafik (Mesh) wird in Python gezeichnet
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0 # Transparent, nur Platzhalter

<AlbumView>:
    # Das ist die Haupt-RecycleView
    viewclass: 'AccuratePerspective'
    RecycleBoxLayout:
        # NUR DIESES EINE Widget darf hier als Kind stehen!
        default_size: None, dp(250)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: dp(10)
''')

class AccuratePerspective(Widget):
    image_source = StringProperty('')
    angle_deg = NumericProperty(0)
    distance = NumericProperty(100)
    richtung = StringProperty('neutral')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.standard_side_length = 200
        self.default_distance = 100
        
        with self.canvas:
            PushMatrix()
            self.pos_transformation = Translate(0, 0)
            self.mesh = Mesh(
                indices=[0, 1, 2, 3],
                mode='triangle_strip',
                vertices=[0]*16 
            )
            PopMatrix()

    def on_image_source(self, instance, value):
        if value and os.path.exists(value):
            try:
                # Textur laden
                self.mesh.texture = CoreImage(value).texture
                self.update_mesh()
            except Exception as e:
                print(f"Ladefehler: {e}")

    def on_pos(self, *args):
        # Dynamische Neigung basierend auf der Position
        # Angenommen das Fenster ist 600px hoch, Mitte = 300
        diff = self.y - 250 
        if diff > 50:
            self.richtung = 'vor'
            self.angle_deg = min(25, diff * 0.1)
        elif diff < -50:
            self.richtung = 'zurueck'
            self.angle_deg = min(25, abs(diff) * 0.1)
        else:
            self.richtung = 'neutral'
            self.angle_deg = 0
        self.update_mesh()

    def update_mesh(self):
        # Deine mathematische Logik (gekürzt für Stabilität)
        new_angle = math.radians(self.angle_deg)
        s = self.standard_side_length
        d = 0 # Vereinfacht
        
        # Berechnung der Vertices (Deine Logik hier einsetzen)
        delta_h = abs(math.sin(new_angle) * 30)
        
        if self.richtung == 'vor':
            v = [0, s, 0, 0,  s, s, 1, 0,  delta_h, delta_h, 0, 1,  s-delta_h, delta_h, 1, 1]
        elif self.richtung == 'zurueck':
            v = [delta_h, s-delta_h, 0, 0,  s-delta_h, s-delta_h, 1, 0,  0, 0, 0, 1,  s, 0, 1, 1]
        else:
            v = [0, s, 0, 0,  s, s, 1, 0,  0, 0, 0, 1,  s, 0, 1, 1]
        
        self.mesh.vertices = v

class AlbumView(RecycleView):
    def __init__(self, **kwargs):
        super(AlbumView, self).__init__(**kwargs)
        # Hier deine echte Suche einbauen:
        # self.image_paths = self.find_image_files_multiple_globs('Music_Library')
        # Für den Test nehmen wir 1000 Dummy-Einträge:
        self.data = [{'image_source': 'dein_test_bild.jpg'} for i in range(1000)]

class MusicApp(App):
    def build(self):
        # Wir geben die AlbumView zurück, die durch Builder konfiguriert wurde
        return AlbumView()

if __name__ == '__main__':
    MusicApp().run()