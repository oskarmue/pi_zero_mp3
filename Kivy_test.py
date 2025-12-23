'''
virtuelle umgebung muss vor ausführen des programms und pip befehlen activiert werden (im Projektordner)
source venv/bin/activate
'''


#Imports
import glob
import os

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window

from kivy.graphics import RenderContext, Color, Rectangle, BindTexture
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock


#Settings
Window.borderless = True


class PerspectiveImage(Image):
    def __init__(self, **kwargs):
        self.canvas = RenderContext(use_parent_projection=True)
        super(PerspectiveImage, self).__init__(**kwargs)
        # Wir rufen die Transformation regelmäßig auf, falls sich die Größe ändert
        Clock.schedule_once(self.setup_projection, 0)

    def setup_projection(self, *args):
        # 1. Projektionsmatrix (Perspektive)
        # fovy=45, aspect=ratio, near=0.1, far=100
        projection = Matrix()
        projection.perspective(10, self.width / self.height, 0.1, 100.0)
        
        # 2. Modelview-Matrix (Rotation und Positionierung)
        modelview = Matrix()
        # Wir schieben das Bild auf der Z-Achse nach hinten, damit es sichtbar wird
        modelview.translate(0, 0, -1.5) 
        # Drehung um 45 Grad um die Y-Achse für den 3D-Effekt
        modelview.rotate(10, 0, 1, 0) 

        self.canvas['projection_mat'] = projection
        self.canvas['modelview_mat'] = modelview



#Code
class ImageViewerApp(App):
    def build(self):

        self.image_paths = self.find_image_files_multiple_globs('Music_Library')
        
        Window.size = (1350, 1600)

        layout = FloatLayout()

        # Bild in der Mitte des Fensters anzeigen
        self.image_widget = Image(size_hint=(None, None), size=(Window.width, Window.height))
        self.load_image(self.image_paths[0])  # Erstes Bild laden

        self.perspective_img = PerspectiveImage(
            source=self.image_paths[0],
            size_hint=(0.5, 1),
            pos_hint={'x': 0.5, 'y': 0}
        )




        #layout.add_widget(self.image_widget)
        layout.add_widget(self.perspective_img)

        return layout
    

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
        
        return all_image_files

    def load_image(self, image_path):
        #Lädt das Bild und zeigt es im Kivy-Image-Widget an
        self.image_widget.source = image_path

    

if __name__ == '__main__':
    ImageViewerApp().run()

