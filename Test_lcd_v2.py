#scp /home/om/Desktop/Cover_Flow_test/Test_lcd_v2.py pi@192.168.2.126:/home/pi/Cover_Flow_test/
import os

# WICHTIG: Erzwinge die Nutzung des Framebuffers/KMS
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_GL_BACKEND'] = 'gl' # oder 'gles' bei Problemen
os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image # Neu: Das Image-Widget
from kivy.uix.floatlayout import FloatLayout # Neu: FloatLayout

image_path = '/home/pi/Cover_Flow_test/Music_Library/Eminem/Encore/ab67616d000082c1dfd0ebe9b4b99f621f376453_passend.jpeg'

class SimpleApp(App):
    def build(self):
        layout = FloatLayout()

        # Ein Bild-Widget hinzufügen
        # 'source' ist der Pfad zu deiner Bilddatei (z.B. .png oder .jpg)
        oskar_bild = Image(
            source='/home/pi/Cover_Flow_test/Music_Library/Eminem/Encore/ab67616d000082c1dfd0ebe9b4b99f621f376453_passend.jpeg', # Ersetze dies durch deinen Dateinamen
            size_hint=(0.5, 0.5),    # Das Bild nimmt 50% des Platzes ein
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )

        # Dein Label darunter
        label = Label(
            text='Hier spricht Oskar', 
            font_size='30sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )

        layout.add_widget(oskar_bild)
        layout.add_widget(label)

        return layout

if __name__ == '__main__':
    SimpleApp().run()
