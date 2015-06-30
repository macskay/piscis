from os import path
from tkinter import Toplevel
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo
from tkinter.ttk import Style
from pygubu import TkApplication, Builder
from piscis.model import PredatorFactory

SCRIPT_DIR = path.dirname(path.abspath(__file__))
BACKGROUND_COLOR = "#FFFFFF"

# noinspection PyAttributeOutsideInit
class MainWindow(TkApplication):
    def _create_ui(self):
        self.pygubu_builder = Builder()
        self.pygubu_builder.add_from_file(path.join(SCRIPT_DIR, "forms", "main_window.ui"))

        # self.secondary_window = SecondaryWindow(Toplevel())

        self.predator_factory = PredatorFactory()

        self.setup()

    def setup(self):
        self.set_title("Piscis")

        self.pygubu_builder.get_object('main_frame', self.master)
        self.set_menu(self.pygubu_builder.get_object('main_menu', self.master))

        self.create_tabs()

        self.pygubu_builder.connect_callbacks(self)

    def create_tabs(self):
        self._create_canvas_tab('tab_all_screens')
        self._create_canvas_tab('tab_single_tab_one')
        self._create_canvas_tab('tab_single_tab_two')
        self._create_canvas_tab('tab_single_tab_three')
        self._create_canvas_tab('tab_single_tab_four')

    def _create_canvas_tab(self, identifier):
        if identifier == 'tab_all_screens':
            AllCanvasTab(self.pygubu_builder.get_object(identifier, self.master))
        else:
            SingleCanvasTab(self.pygubu_builder.get_object(identifier, self.master), self)

    def on_about(self):
        showinfo("Piscis", "Piscis - 1.0\nContact: soojin.ryu@mpimf-heidelberg.mpg.de")

    def on_exit(self):
        self.master.quit()

    def on_fullscreen(self):
        self.secondary_window.set_fullscreen()

    def on_change_fullscreen(self):
        new_color = askcolor(color=self.secondary_window.current_background_color, title="Change Background-Color")[1]
        self.secondary_window.change_background_color(new_color)

    def create_predator(self, color, target_diameter, scaling_velocity):
        self.predator_factory.target_diameter = target_diameter
        self.predator_factory.scaling_velocity = scaling_velocity
        self.predator_factory.color = color

        print("Create Predator with following settings:")
        print("Scaling-Velocity: ", self.predator_factory.scaling_velocity)
        print("Target-Diameter: ", self.predator_factory.target_diameter)
        print("Predator-Color: ", self.predator_factory.color, "\n")

        # self.predator = self.predator_factory.create()

    def get_predator_color(self):
        return self.predator_factory.color

# noinspection PyAttributeOutsideInit
class SingleCanvasTab(TkApplication):
    def __init__(self, master, parent=None):
        TkApplication.__init__(self, master)
        self.parent = parent

        self.target_diameter = 0
        self.scaling_velocity = 0
        self.color = BACKGROUND_COLOR

    def _create_ui(self):
        self.pygubu_builder = Builder()
        self.pygubu_builder.add_from_file(path.join(SCRIPT_DIR, "forms", "single_canvas_tab.ui"))

        self.setup()

    def setup(self):
        self.canvas = self.pygubu_builder.get_object('canvas', self.master)

        self.current_background_color = BACKGROUND_COLOR
        self.change_background_color(self.current_background_color)

        self._create_scale_slider()
        self._create_speed_slider()
        self._create_buttons()

        self.pygubu_builder.connect_callbacks(self)

    def _create_scale_slider(self):
        self.pygubu_builder.get_object('scale_label', self.master)
        self.pygubu_builder.get_object('scale_slider', self.master)

    def _create_speed_slider(self):
        self.pygubu_builder.get_object('speed_label', self.master)
        self.pygubu_builder.get_object('speed_slider', self.master)

    def _create_buttons(self):
        self.pygubu_builder.get_object('background', self.master)
        self.pygubu_builder.get_object('stimuli_color', self.master)
        self.pygubu_builder.get_object('generate', self.master)

    def on_generate(self):
        self.parent.create_predator(self.color, self.target_diameter, self.scaling_velocity)

    def on_background(self):
        new_color = askcolor(color=self.current_background_color, title="Change Background-Color")[1]
        self.change_background_color(new_color)

    def on_stimuli_color(self):
        new_color = askcolor(color=self.parent.get_predator_color(), title="Change Predator-Color")[1]
        # self.parent.set_predator_color(new_color)
        self.color = new_color

    def on_scale_slider(self, value):
        # self.parent.set_predator_target_diameter(value)
        self.target_diameter = value

    def on_speed_slider(self, value):
        # self.parent.set_predator_scaling_velocity(value)
        self.scaling_velocity = value

    def change_background_color(self, color):
        self.canvas.configure(background=color)
        self.current_background_color = color

class AllCanvasTab(TkApplication):
    def _create_ui(self):
        self.pygubu_builder = Builder()
        self.pygubu_builder.add_from_file(path.join(SCRIPT_DIR, "forms", "all_screens_tab.ui"))

        self.setup()

    def setup(self):
        self._create_canvas('canvas_one')
        self._create_canvas('canvas_two')
        self._create_canvas('canvas_three')
        self._create_canvas('canvas_four')

    def _create_canvas(self, identifier):
        self.pygubu_builder.get_object(identifier, self.master)
        self.pygubu_builder.get_object(identifier+'_label', self.master)


# noinspection PyAttributeOutsideInit
class SecondaryWindow(TkApplication):
    def _create_ui(self):
        self.pygubu_builder = Builder()
        self.pygubu_builder.add_from_file(path.join(SCRIPT_DIR, "forms", "secondary_window.ui"))

        self.style = Style()

        self.current_background_color = BACKGROUND_COLOR

        self.setup()

    def setup(self):
        self.set_title("Piscis")
        self.pygubu_builder.get_object('main_frame', self.master)
        self.change_background_color(BACKGROUND_COLOR)

    def set_fullscreen(self):
        self.master.overrideredirect(True)
        self.master.geometry("%dx%d+0+0" % (self.master.winfo_screenwidth(), self.master.winfo_screenheight()))

    def change_background_color(self, color):
        self.style.configure('TFrame', background=color)
        self.current_background_color = color