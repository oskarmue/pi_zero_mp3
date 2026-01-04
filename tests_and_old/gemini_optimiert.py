import glob
import os
import math
from collections import deque
import psutil
from kivy.config import Config
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Mesh, Translate, PushMatrix, PopMatrix
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage

# Fenster-Einstellungen
Config.set('graphics', 'width', '240')
Config.set('graphics', 'height', '320')
Config.set('graphics', 'resizable', False)
Window.borderless = True

class AccuratePerspective(Widget):
    def __init__(self, image_path, resolution, widget_breite, **kwargs):
        super().__init__(**kwargs)
        self.widget_breite = widget_breite
        self.resolution = resolution
        
        # Initialisierung mit Dummy-Vertices
        with self.canvas:
            PushMatrix()
            self.pos_transformation = Translate(0, 0)
            self.mesh = Mesh(
                vertices=[0]*((resolution+1)**2 * 4),
                indices=[0]*(resolution**2 * 6),
                mode='triangles',
                texture=CoreImage(image_path).texture
            )
            PopMatrix()

    def change_position(self, new_x, new_y):
        self.pos_transformation.x = new_x
        self.pos_transformation.y = new_y

    def change_perspective(self, new_vertices):
        self.mesh.vertices = new_vertices

    def change_texture(self, image_path):
        if os.path.exists(image_path):
            self.mesh.texture = CoreImage(image_path).texture

    # Die Geometrie-Funktionen (forward_lean, backward_lean etc.) bleiben wie in deinem Original
    def calc_dh(self, default_distance, distance, angle_in_dec, widget_seitenlänge):
        entfernungs_skalier_faktor = distance/default_distance
        new_angle = math.radians(angle_in_dec)
        delta_h = widget_seitenlänge*(1-math.cos(new_angle)) * entfernungs_skalier_faktor
        return round(delta_h * entfernungs_skalier_faktor)

    def vertices_an_distance_anpassen(self, resolution, widgetbreite, default_distance, new_distance, vertices):
        widgetbreite_halbiert = round(widgetbreite/2)
        indices = []
        for i in range(resolution):
            for j in range(resolution):
                bl = i * (resolution + 1) + j
                br = bl + 1
                tl = bl + (resolution + 1)
                tr = tl + 1
                indices += [bl, br, tr, bl, tr, tl]
        
        vertices_nach_wechsel = vertices[:]
        new_sidelength_diff_by_half = round((widgetbreite - (widgetbreite * default_distance)/new_distance)/2)
        for i in range(0, len(vertices), 4):
            x, y = vertices[i], vertices[i+1]
            if x <= widgetbreite_halbiert:
                vertices_nach_wechsel[i] = round(x + new_sidelength_diff_by_half * (widgetbreite_halbiert - x)/widgetbreite_halbiert)
                vertices_nach_wechsel[i+1] = round(y + (new_sidelength_diff_by_half * (widgetbreite_halbiert - y)/widgetbreite_halbiert if y <= widgetbreite_halbiert else -new_sidelength_diff_by_half * (y - widgetbreite_halbiert)/widgetbreite_halbiert))
            else:
                vertices_nach_wechsel[i] = round(x - new_sidelength_diff_by_half * (x - widgetbreite_halbiert)/widgetbreite_halbiert)
                vertices_nach_wechsel[i+1] = round(y + (new_sidelength_diff_by_half * (widgetbreite_halbiert - y)/widgetbreite_halbiert if y <= widgetbreite_halbiert else -new_sidelength_diff_by_half * (y - widgetbreite_halbiert)/widgetbreite_halbiert))
        return indices, vertices, vertices_nach_wechsel

    def forward_punkte_berechnen_(self, resolution, widgetbreite, db_halbe, dh):
        step_in_percent = 1 / resolution
        step_in_pixel = widgetbreite / resolution
        widgetbreite_halbiert = widgetbreite / 2
        vertices = []
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                vertices += [round(j * step_in_pixel), round(i * step_in_pixel), round(j * step_in_percent, 2), round(1 - i * step_in_percent, 2)]
        
        indices = []
        for i in range(resolution):
            for j in range(resolution):
                bl = i * (resolution+1)+j; br = bl+1; tl = bl+(resolution+1); tr = tl+1
                indices += [bl, br, tr, bl, tr, tl]

        untere_punkte = vertices[:(resolution + 1) * 4]
        obere_punkte = vertices[-(resolution + 1) * 4:]
        winkel = []
        stauchungsfaktor = db_halbe / widgetbreite_halbiert
        for j in range(resolution + 1):
            x_u = round(j * step_in_pixel)
            if x_u < widgetbreite_halbiert: x_u -= stauchungsfaktor * (widgetbreite_halbiert - x_u)
            else: x_u -= stauchungsfaktor * (x_u - widgetbreite_halbiert)
            dx = x_u - round(j * step_in_pixel)
            dy = (0 + dh) - 0
            winkel.append(math.atan(dx/dy) if dy != 0 else 0)

        vertices_nach_wechsel = []
        for i in range(resolution + 1):
            y_verh = i * step_in_percent
            y_koor = i * step_in_pixel + dh * (1 - y_verh)
            for j in range(resolution + 1):
                x_koor = j * step_in_pixel
                verschiebung = math.tan(winkel[j]) * (1 - y_verh) * widgetbreite
                vertices_nach_wechsel += [round(x_koor + verschiebung if x_koor < widgetbreite_halbiert else x_koor - verschiebung), round(y_koor), round(j * step_in_percent, 2), round(1 - y_verh, 2)]
        return indices, vertices, vertices_nach_wechsel

    def backward_punkte_berechnen_(self, resolution, widgetbreite, db_halbe, dh):
        step_in_percent = 1/resolution
        step_in_pixel = widgetbreite/resolution
        widgetbreite_halbiert = widgetbreite/2
        vertices = []
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                vertices += [round(j * step_in_pixel), round(i * step_in_pixel), round(j * step_in_percent, 2), round(1 - i * step_in_percent, 2)]
        indices = []
        for i in range(resolution):
            for j in range(resolution):
                bl = i*(resolution+1)+j; br=bl+1; tl=bl+(resolution+1); tr=tl+1
                indices += [bl, br, tr, bl, tr, tl]
        
        winkel = []
        stauchungsfaktor = db_halbe/widgetbreite_halbiert
        for j in range(resolution + 1):
            x_o = j*step_in_pixel
            if x_o < widgetbreite_halbiert: x_o += stauchungsfaktor * (widgetbreite_halbiert - x_o)
            else: x_o -= stauchungsfaktor * (x_o - widgetbreite_halbiert)
            dx = x_o - j*step_in_pixel
            dy = (widgetbreite - dh) - widgetbreite
            winkel.append(math.atan(dx/dy) if dy != 0 else 0)

        vertices_nach_wechsel = []
        for i in range(resolution+1):
            y_verh = i*step_in_percent
            y_koor = i*step_in_pixel - (dh * y_verh)
            for j in range(resolution+1):
                x_koor = j*step_in_pixel
                verschiebung = math.tan(winkel[j]) * y_koor
                vertices_nach_wechsel += [round(x_koor - verschiebung), round(y_koor), round(j*step_in_percent, 2), round(1-y_verh, 2)]
        return indices, vertices, vertices_nach_wechsel

    def foward_lean(self, default_distance, distance, angle_in_dec, widget_seitenlänge, resolution):
        dh = self.calc_dh(default_distance, distance, angle_in_dec, widget_seitenlänge)
        indices, v_norm, v_gekippt = self.forward_punkte_berechnen_(resolution, widget_seitenlänge, dh/2, dh)
        indices, v_gekippt, v_distant = self.vertices_an_distance_anpassen(resolution, widget_seitenlänge, default_distance, distance, v_gekippt)
        return indices, v_norm, v_gekippt, v_distant

    def backward_lean(self, default_distance, distance, angle_in_dec, widget_seitenlänge, resolution):
        dh = self.calc_dh(default_distance, distance, angle_in_dec, widget_seitenlänge)
        indices, v_norm, v_gekippt = self.backward_punkte_berechnen_(resolution, widget_seitenlänge, dh, dh)
        indices, v_gekippt, v_distant = self.vertices_an_distance_anpassen(resolution, widget_seitenlänge, default_distance, distance, v_gekippt)
        return indices, v_norm, v_gekippt, v_distant

class MyApp(App):
    def build(self):
        self.is_animating = False
        self.distance_background = 120
        self.distance_inbetween = 110
        self.distance_foregorund = 90
        
        # Positionen [x, y, angle, distance, lean_type]
        self.positionen_in_reihenfolge = [
            [60, -60, 30, 120, 0], [60, -30, 30, 120, 0], [60, 0, 30, 120, 0],
            [60, 30, 30, 120, 0], [60, 60, 20, 110, 0], [60, 108, 0, 90, 0],
            [60, 160, 20, 110, 1], [60, 190, 30, 120, 1], [60, 210, 30, 120, 1],
            [60, 240, 30, 120, 1], [60, 270, 30, 120, 1]
        ]

        self.index_of_upper_cover = 0
        self.image_paths = self.find_image_files_multiple_globs('Music_Library')
        self.num_widgets = len(self.positionen_in_reihenfolge)
        self.widgets = deque(maxlen=self.num_widgets)
        
        self.dauer_animation_in_sec = 0.15
        self.frames_per_animation = 10
        self.resolution_ = 1
        self.widget_breite = 120

        self.layout = FloatLayout()
        Window.bind(on_key_down=self.on_key_down)

        # Widgets initialisieren
        for i in range(self.num_widgets):
            img = self.image_paths[i] if i < len(self.image_paths) else self.image_paths[0]
            w = AccuratePerspective(image_path=img, resolution=self.resolution_, widget_breite=self.widget_breite)
            self.widgets.append(w)
            self.apply_state(w, self.positionen_in_reihenfolge[i])
        
        self.reorder_layers()
        self.precompute_animations()
        return self.layout

    def apply_state(self, widget, state):
        x, y, angle, dist, lean = state
        widget.change_position(x, y)
        if lean == 1:
            _, _, _, v = widget.foward_lean(100, dist, angle, self.widget_breite, self.resolution_)
        else:
            _, _, _, v = widget.backward_lean(100, dist, -angle if angle != 0 else 0, self.widget_breite, self.resolution_)
        widget.change_perspective(v)

    def precompute_animations(self):
        self.anim_down = []
        self.anim_up = []
        
        for i in range(self.num_widgets):
            steps_down = []
            steps_up = []
            
            # Ziel-Indizes für Down (+1) und Up (-1)
            idx_next = (i + 1) % self.num_widgets
            idx_prev = (i - 1) % self.num_widgets
            
            s1 = self.positionen_in_reihenfolge[i]
            s_down = self.positionen_in_reihenfolge[idx_next]
            s_up = self.positionen_in_reihenfolge[idx_prev]

            for f in range(1, self.frames_per_animation + 1):
                t = f / self.frames_per_animation
                # Down Interpolation
                state_d = [s1[j] + (s_down[j] - s1[j]) * t for j in range(4)] + [s_down[4]]
                steps_down.append(self.get_vertices_for_state(state_d))
                # Up Interpolation
                state_u = [s1[j] + (s_up[j] - s1[j]) * t for j in range(4)] + [s_up[4]]
                steps_up.append(self.get_vertices_for_state(state_u))
                
            self.anim_down.append(steps_down)
            self.anim_up.append(steps_up)

    def get_vertices_for_state(self, state):
        x, y, angle, dist, lean = state
        dummy = self.widgets[0]
        if lean == 1:
            _, _, _, v = dummy.foward_lean(100, dist, angle, self.widget_breite, self.resolution_)
        else:
            _, _, _, v = dummy.backward_lean(100, dist, -angle, self.widget_breite, self.resolution_)
        return (x, y, v)

    def reorder_layers(self):
        for w in self.widgets:
            if w.parent: self.layout.remove_widget(w)
        # Z-Index: Mitte (5) ganz oben, Ränder ganz unten
        order = [0, 10, 1, 9, 2, 8, 3, 7, 4, 6, 5]
        for idx in order:
            self.layout.add_widget(self.widgets[idx])

    def on_key_down(self, window, key, *args):
        if self.is_animating: return
        if key == 273: self.cover_flow_up()
        elif key == 274: self.cover_flow_down()

    def cover_flow_down(self):
        if self.index_of_upper_cover >= len(self.image_paths) - self.num_widgets: return
        self.is_animating = True
        self.index_of_upper_cover += 1
        self.current_frame = 0
        self.animation_event = Clock.schedule_interval(self.do_anim_down, 1/60)

    def do_anim_down(self, dt):
        if self.current_frame >= self.frames_per_animation:
            self.widgets.rotate(-1) # Logische Verschiebung am Ende
            # Neues Widget am unteren Rand bekommt neue Textur
            new_img_idx = self.index_of_upper_cover + self.num_widgets - 1
            if new_img_idx < len(self.image_paths):
                self.widgets[-1].change_texture(self.image_paths[new_img_idx])
            
            self.reorder_layers()
            self.is_animating = False
            return False
        
        for i in range(self.num_widgets):
            x, y, v = self.anim_down[i][self.current_frame]
            self.widgets[i].change_position(x, y)
            self.widgets[i].change_perspective(v)
        self.current_frame += 1

    def cover_flow_up(self):
        if self.index_of_upper_cover <= 0: return
        self.is_animating = True
        self.index_of_upper_cover -= 1
        self.current_frame = 0
        self.animation_event = Clock.schedule_interval(self.do_anim_up, 1/60)

    def do_anim_up(self, dt):
        if self.current_frame >= self.frames_per_animation:
            self.widgets.rotate(1)
            self.widgets[0].change_texture(self.image_paths[self.index_of_upper_cover])
            self.reorder_layers()
            self.is_animating = False
            return False
        
        for i in range(self.num_widgets):
            x, y, v = self.anim_up[i][self.current_frame]
            self.widgets[i].change_position(x, y)
            self.widgets[i].change_perspective(v)
        self.current_frame += 1

    def find_image_files_multiple_globs(self, directory):
        patterns = ["**/*.jpg", "**/*.jpeg", "**/*.png"]
        files = []
        for p in patterns:
            files.extend(glob.glob(os.path.join(directory, p), recursive=True))
        return sorted([f for f in files if "_passend" in f])

if __name__ == '__main__':
    MyApp().run()