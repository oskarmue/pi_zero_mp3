'''
virtuelle umgebung muss vor ausführen des programms und pip befehlen activiert werden (im Projektordner)
source venv/bin/activate
'''


#Imports
import glob
import os

import numpy as np
import cv2 as cv

import matplotlib.pyplot as plt
'''
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window

from kivy.graphics import RenderContext, Color, Rectangle, BindTexture
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock


#Settings
Window.borderless = True
'''
pfad = 'test_image.jpeg'

img = cv.imread(pfad)
assert img is not None, "file could not be read, check with os.path.exists()"
rows,cols,ch = img.shape


pts1 = np.float32([[0,0],[1500,0],[0,1500],[1500,1500]])
pts2 = np.float32([[0,250],[1500,0],[0,1250],[1500,1500]])
pts3 = np.float32([[100,250],[1400,100],[100,1250],[1400,1400]])
pts4 = np.float32([[0,300],[2000,0],[0,1200],[2000,1500]])

M_1 = cv.getPerspectiveTransform(pts1,pts2)
M_2 = cv.getPerspectiveTransform(pts1,pts3)
M_3 = cv.getPerspectiveTransform(pts1,pts4)


dst_1 = cv.warpPerspective(img,M_1,(1500,1500))
dst_2 = cv.warpPerspective(img,M_2,(1500,1500))
dst_3 = cv.warpPerspective(img,M_3,(2000,1500))

plt.subplot(141),plt.imshow(img),plt.title('Input')
plt.subplot(142),plt.imshow(dst_1),plt.title('Output_1')
plt.subplot(143),plt.imshow(dst_2),plt.title('Output_2')
plt.subplot(144),plt.imshow(dst_3),plt.title('Output_3')
plt.show()

'''
#Code
class ImageViewerApp(App):
    def build(self):

        self.image_paths = self.find_image_files_multiple_globs('Music_Library')
        print(self.image_paths[0])

        Window.size = (1350, 1600)

        layout = FloatLayout()

        # Bild in der Mitte des Fensters anzeigen
        self.image_widget = Image(size_hint=(None, None), size=(Window.width, Window.height))
        self.load_image(self.image_paths[0])  # Erstes Bild laden



        layout.add_widget(self.image_widget)

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

'''