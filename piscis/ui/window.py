from os import path
import random
from tkinter import Toplevel, ALL
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo
from tkinter.ttk import Style
from pygubu import TkApplication, Builder
import time
from piscis.model import PredatorFactory

SCRIPT_DIR = path.dirname(path.abspath(__file__))
BACKGROUND_COLOR = "#FFFFFF"
PREDATOR_COLOR = "#000000"


# noinspection PyAttributeOutsideInit
class MainWindow(TkApplication):
    def _create_ui(self):
        self.pygubu_builder = Builder()
        self.pygubu_builder.add_from_file(path.join(SCRIPT_DIR, "forms", "main_window.ui"))

        self.secondary_window = SecondaryWindow(Toplevel())
        self.secondary_window.master.withdraw()

        self.predator = [None, None, None, None]
        self.current_tab = 0
        self.tabs = list()
        self.all_tab = None
        self.after_id = 0

        self.predator_factory = PredatorFactory()

        self.setup()

    def setup(self):
        self.set_title("Piscis")

        self.pygubu_builder.get_object('main_frame', self.master)
        self.set_menu(self.pygubu_builder.get_object('main_menu', self.master))

        self.create_tabs()

        self.pygubu_builder.connect_callbacks(self)

        # self.start_update()

    def create_tabs(self):
        self.all_tab = self._create_canvas_tab('tab_all_screens')
        self.tabs.append(self._create_canvas_tab('tab_single_tab_one'))
        self.tabs.append(self._create_canvas_tab('tab_single_tab_two'))
        self.tabs.append(self._create_canvas_tab('tab_single_tab_three'))
        self.tabs.append(self._create_canvas_tab('tab_single_tab_four'))

    def _create_canvas_tab(self, identifier):
        if identifier == 'tab_all_screens':
            return AllCanvasTab(self.pygubu_builder.get_object(identifier, self.master))
        else:
            self.current_tab += 1
            return SingleCanvasTab(self.pygubu_builder.get_object(identifier, self.master), self.current_tab-1, self)

    @staticmethod
    def on_about():
        showinfo("Piscis", "Piscis - 1.0\nContact: soojin.ryu@mpimf-heidelberg.mpg.de")

    def on_exit(self):
        self.master.quit()

    def on_fullscreen(self):
        self.secondary_window.set_fullscreen()

    def on_change_fullscreen(self):
        new_color = askcolor(color=self.secondary_window.current_background_color, title="Change Background-Color")[1]
        self.secondary_window.change_background_color(new_color)

    def create_predator(self, color, target_diameter, scaling_velocity, starting_position=None):
        if starting_position is None:
            starting_position = random.random(), random.random()

        self.predator_factory.starting_position = starting_position
        self.predator_factory.target_diameter = target_diameter
        self.predator_factory.scaling_velocity = scaling_velocity
        self.predator_factory.color = color

        return self.predator_factory.create()

    def get_predator_color(self):
        return self.predator_factory.color

    def start_predator(self, predator, id_number):
        if predator is None:
            showinfo("No Predator found", "Please place a stimuli first!")
            return
        now = int(time.time()*1000)
        predator.start_scaling(now)
        self.predator[id_number] = predator
        self.start_update()

    def start_update(self):
        self.after_id = self.master.after(25, self.update)

    def update(self):
        self.after_id = self.master.after(25, self.update)
        self.render()

    def stop_update(self):
        self.master.after_cancel(self.after_id)

    def render(self):
        for i, item in enumerate(self.predator):
            if item is not None:
                drawer = PredatorDrawer(item)
                drawer.draw_predator(self.tabs[i], self.all_tab, self.secondary_window, i)

    def change_background_color_of_all_canvas(self, id_number, color):
        self.all_tab.change_background(id_number, color)
        self.secondary_window.change_canvas_background(id_number, color)


# noinspection PyAttributeOutsideInit
class SingleCanvasTab(TkApplication):
    def __init__(self, master, id_number, parent=None):
        TkApplication.__init__(self, master)
        self.id_number = id_number
        self.parent = parent

        self.change_background_color(self.current_background_color)
        self.target_diameter = 0
        self.scaling_velocity = 0

        self.predator = None
        self.predator_draw_object = None

        self.starting_position = None

    def _create_ui(self):
        self.pygubu_builder = Builder()
        self.pygubu_builder.add_from_file(path.join(SCRIPT_DIR, "forms", "single_canvas_tab.ui"))

        self.setup()

    def setup(self):
        self.canvas = self.pygubu_builder.get_object('canvas', self.master)
        self.canvas.bind("<Button-1>", self.set_starting_position)

        self.current_background_color = BACKGROUND_COLOR
        self.color = PREDATOR_COLOR

        self._create_scale_slider()
        self._create_speed_slider()
        #self._create_buttons()
        self._create_interval_controls()

        self.pygubu_builder.connect_callbacks(self)

    def set_starting_position(self, event):
        self.starting_position = event.x/self.canvas.winfo_width(), event.y/self.canvas.winfo_height()
        self.on_generate()

    def _create_scale_slider(self):
        self.pygubu_builder.get_object('scale_slider', self.master)

    def _create_speed_slider(self):
        self.pygubu_builder.get_object('speed_slider', self.master)

    def _create_buttons(self):
        self.pygubu_builder.get_object('background', self.master)
        self.pygubu_builder.get_object('stimuli_color', self.master)
        self.pygubu_builder.get_object('generate', self.master)
        self.pygubu_builder.get_object('start_stimulation', self.master)
        self.pygubu_builder.get_object('stop_stimulation', self.master)

    def _create_interval_controls(self):
        self.pygubu_builder.get_object('pause_seconds', self.master)
        self.pygubu_builder.get_object('interval_pause_seconds', self.master)
        self.pygubu_builder.get_object('interval_duration_seconds', self.master)
        self.pygubu_builder.get_object('duration_seconds', self.master)

    def on_generate(self):
        self.canvas.delete(self.predator_draw_object)
        self.predator = self.parent.create_predator(self.color, self.target_diameter, self.scaling_velocity,
                                                    self.starting_position)
        drawer = PredatorDrawer(self.predator)
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        begin_x, begin_y, end_x, end_y = drawer.calculate_coordinates(width, height, self.target_diameter)
        self.predator_draw_object = self.canvas.create_oval(begin_x, begin_y, end_x,
                                                            end_y,
                                                            fill=self.color, outline=self.color)
        self.starting_position = None

    def on_background(self):
        new_color = askcolor(color=self.current_background_color, title="Change Background-Color")[1]
        self.change_background_color(new_color)

    def on_stimuli_color(self):
        new_color = askcolor(color=self.parent.get_predator_color(), title="Change Predator-Color")[1]
        self.color = new_color
        if self.predator is not None:
            self.predator.color = self.color

    def on_scale_slider(self, value):
        self.target_diameter = float(value)
        if self.predator is not None:
            self.predator.set_target_diameter(self.target_diameter)

    def on_speed_slider(self, value):
        self.scaling_velocity = float(value)/5
        if self.predator is not None:
            self.predator.set_scaling_velocity(self.scaling_velocity)

    def on_start(self):
        self.parent.start_predator(self.predator, self.id_number)

    def on_stop(self):
        self.parent.stop_update()

    def on_duration_change(self):
        print("Test")

    def change_background_color(self, color):
        self.canvas.configure(background=color)
        self.parent.change_background_color_of_all_canvas(color, self.id_number)
        self.current_background_color = color



class AllCanvasTab(TkApplication):
    def _create_ui(self):
        self.pygubu_builder = Builder()
        self.pygubu_builder.add_from_file(path.join(SCRIPT_DIR, "forms", "all_screens_tab.ui"))
        self.canvas = list()
        self.predator_draw_object = [None, None, None, None]
        self.setup()

    def setup(self):
        self.canvas.append(self._create_canvas('canvas_one'))
        self.canvas.append(self._create_canvas('canvas_two'))
        self.canvas.append(self._create_canvas('canvas_three'))
        self.canvas.append(self._create_canvas('canvas_four'))

    def _create_canvas(self, identifier):
        self.pygubu_builder.get_object(identifier+'_label', self.master)
        return self.pygubu_builder.get_object(identifier, self.master)

    def change_background(self, color, id_number):
        self.canvas[id_number].configure(background=color)


# noinspection PyAttributeOutsideInit
class SecondaryWindow(TkApplication):
    def _create_ui(self):
        self.pygubu_builder = Builder()
        self.pygubu_builder.add_from_file(path.join(SCRIPT_DIR, "forms", "secondary_window.ui"))

        self.style = Style()

        self.canvas = list()
        self.predator_draw_object = [None, None, None, None]

        self.current_background_color = BACKGROUND_COLOR

        self.setup()

    def setup(self):
        self.set_title("Piscis")
        self.pygubu_builder.get_object('main_frame', self.master)

        self.canvas.append(self._create_canvas('canvas_one'))
        self.canvas.append(self._create_canvas('canvas_two'))
        self.canvas.append(self._create_canvas('canvas_three'))
        self.canvas.append(self._create_canvas('canvas_four'))

        self.change_background_color(BACKGROUND_COLOR)

    def _create_canvas(self, identifier):
        return self.pygubu_builder.get_object(identifier, self.master)

    def set_fullscreen(self):
        self.master.overrideredirect(True)
        self.master.geometry("%dx%d+0+0" % (self.master.winfo_screenwidth(), self.master.winfo_screenheight()))

    def change_background_color(self, color):
        self.style.configure('TFrame', background=color)
        self.current_background_color = color

    def change_canvas_background(self, color, id_number):
        self.canvas[id_number].configure(background=color)


class PredatorDrawer(object):
    def __init__(self, predator):
        self.predator = predator

    def draw_predator(self, tab, all_tab, secondary, index):
        self.render(tab)
        self.render_copy_canvases(all_tab, index)
        self.render_copy_canvases(secondary, index)

    def render(self, tab):  # pragma: no cover
        tab.canvas.delete(ALL)
        tab.predator_draw_object = self.render_predator(tab.canvas)

    def render_copy_canvases(self, copy_screen, index):  # pragma: no cover
        copy_screen.canvas[index].delete(ALL)
        copy_screen.predator_draw_object[index] = self.render_predator(copy_screen.canvas[index])

    def render_predator(self, canvas):  # pragma: no cover
        now = int(time.time()*1000)
        width, height = canvas.winfo_width(), canvas.winfo_height()
        begin_x, begin_y, end_x, end_y = \
            self.calculate_coordinates(width, height, self.predator.get_current_diameter(now))

        return canvas.create_oval(begin_x, begin_y, end_x, end_y, fill=self.predator.color, outline=self.predator.color)

    def calculate_coordinates(self, width, height, current_diameter):  # pragma: no cover
        begin_x, begin_y = width*self.predator.get_starting_position()[0], \
                           height*self.predator.get_starting_position()[1]
        end_x, end_y = begin_x+current_diameter*width, begin_y+current_diameter*width

        pred_width, pred_height = end_x - begin_x, end_y - begin_y

        begin_x -= pred_width // 2
        begin_y -= pred_height // 2

        end_x -= pred_width // 2
        end_y -= pred_height // 2

        return begin_x, begin_y, end_x, end_y
