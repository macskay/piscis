from os import path
import random
from sched import scheduler
from threading import Timer
from tkinter import Toplevel, ALL
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo
from tkinter.ttk import Style
from pygubu import TkApplication, Builder
import time
from piscis.model import PredatorFactory
from apscheduler.schedulers.background import BackgroundScheduler

MIN_TO_SEC = 60

SCRIPT_DIR = path.dirname(path.abspath(__file__))
BACKGROUND_COLOR = "#FFFFFF"
PREDATOR_COLOR = "#000000"

VERTICAL_Y_MARGIN = 0.15
VERTICAL_X_MARGIN = 0.014
HORIZONTAL_Y_MARGIN = 0.044
HORIZONTAL_X_MARGIN = 0.09

PISCIS_TITLE = "Piscis"
PISCIS_VERSION = "1.0"
PISCIS_CONTACT = "Contact: soojin.ryu@mpimf-heidelberg.mpg.de"

# noinspection PyAttributeOutsideInit
class MainWindow(TkApplication):
    def _create_ui(self):
        self.pygubu_builder = Builder()
        self.pygubu_builder.add_from_file(path.join(SCRIPT_DIR, "forms", "main_window.ui"))

        self.secondary_window = SecondaryWindow(Toplevel())
        # self.secondary_window.master.withdraw()

        self.predator = [None, None, None, None]
        self.drawer = PredatorDrawer(None)
        self.current_tab = 0
        self.tabs = list()
        self.remaining_secs = 0
        self.all_tab = None
        self.after_id = 0

        self.isDrawOnAllScreenActive = [True, True, True, True]

        self.predator_factory = PredatorFactory()

        self.setup()

    def setup(self):
        self.set_title(PISCIS_TITLE)

        self.pygubu_builder.get_object('main_frame', self.master)
        self.set_menu(self.pygubu_builder.get_object('main_menu', self.master))

        self.create_tabs()

        self.pygubu_builder.connect_callbacks(self)

        for i, item in enumerate(self.predator):
            draw_all_outlines(self.tabs[i], self.all_tab, self.secondary_window, i)

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
            return SingleCanvasTab(self.pygubu_builder.get_object(identifier, self.master), self.current_tab - 1, self)

    @staticmethod
    def on_about():
        showinfo(PISCIS_TITLE, PISCIS_TITLE + " - " + PISCIS_VERSION + "\n" + PISCIS_CONTACT)

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
        self.isDrawOnAllScreenActive[id_number] = True
        predator.start_scaling(int(time.time() * 1000))
        self.predator[id_number] = predator
        self.drawer.start()
        self.start_update()

    def start_update(self):
        self.after_id = self.master.after(25, self.update)

    def update(self):
        self.after_id = self.master.after(25, self.update)
        self.render()

    def render(self):
        for i, item in enumerate(self.predator):
            self.draw_predators(i, item)
            # self.drawer.draw_all_outlines(self.tabs[i], self.all_tab, self.secondary_window, i)

    def draw_predators(self, i, item):
        if item is not None:
            self.drawer.predator = item
            self.draw_predators_on_all_screens(i)

    def draw_predators_on_all_screens(self, i):
        if self.isDrawOnAllScreenActive[i]:
            self.drawer.draw_predator(self.tabs[i], self.all_tab, self.secondary_window, i)

    def change_background_color_of_all_canvas(self, id_number, color):
        self.all_tab.change_background(id_number, color)
        self.secondary_window.change_canvas_background(id_number, color)

    def stop_drawing(self):
        self.drawer.stop()


# noinspection PyAttributeOutsideInit
class SingleCanvasTab(TkApplication):
    def __init__(self, master, id_number, parent=None):
        TkApplication.__init__(self, master)
        self.id_number = id_number
        self.parent = parent

        self.change_background_color(self.current_background_color)
        self.target_diameter = 0
        self.scaling_velocity = 0

        self.remaining_secs_run = 0
        self.remaining_secs_pause = 0

        self.predator = None
        self.predator_draw_object = None

        self.starting_position = None

        self.run_timer = None
        self.pause_timer = None

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
        self._create_interval_controls()
        self._create_buttons()

        self.pygubu_builder.connect_callbacks(self)

    def _create_scale_slider(self):
        self.pygubu_builder.get_object('scale', self.master)

    def _create_speed_slider(self):
        self.pygubu_builder.get_object('speed', self.master)

    def _create_interval_controls(self):
        self.pygubu_builder.get_object('interval', self.master)
        self.pygubu_builder.get_object('interval_run', self.master)
        self.pygubu_builder.get_object('interval_pause', self.master)

        self._create_running_interval_settings()
        self._create_pausing_interval_settings()

    def _create_pausing_interval_settings(self):
        self.interval_seconds_pause = self.pygubu_builder.get_object('spin_seconds_pause', self.master)
        self.interval_minutes_pause = self.pygubu_builder.get_object('spin_minutes_pause', self.master)
        self.remaining_secs_label_pause = self.pygubu_builder.get_object('remaining_secs_pause', self.master)

    def _create_running_interval_settings(self):
        self.interval_seconds_run = self.pygubu_builder.get_object('spin_seconds_run', self.master)
        self.interval_minutes_run = self.pygubu_builder.get_object('spin_minutes_run', self.master)
        self.remaining_secs_label_run = self.pygubu_builder.get_object('remaining_secs_run', self.master)

    def _create_buttons(self):
        self.pygubu_builder.get_object('background', self.master)
        self.pygubu_builder.get_object('stimuli_color', self.master)
        self.pygubu_builder.get_object('generate', self.master)
        self.pygubu_builder.get_object('simulate', self.master)

    def on_generate(self):
        self.canvas.delete(self.predator_draw_object)
        self.predator = self.parent.create_predator(self.color, self.target_diameter, self.scaling_velocity,
                                                    self.starting_position)
        self.draw_preview_predator()
        self.parent.isDrawOnAllScreenActive[self.id_number] = False
        self.starting_position = None

    def draw_preview_predator(self):
        drawer = PredatorDrawer(self.predator)
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        begin_x, begin_y, end_x, end_y = drawer.calculate_coordinates(width, height, self.target_diameter)
        self.predator_draw_object = self.canvas.create_oval(begin_x, begin_y, end_x,
                                                            end_y,
                                                            fill=self.color, outline=self.color)

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
        self.scaling_velocity = float(value) / 5
        if self.predator is not None:
            self.predator.set_scaling_velocity(self.scaling_velocity)

    def on_start(self):
        self.parent.start_predator(self.predator, self.id_number)
        if self.remaining_secs_run > 0:
            self.update_pause_remaining_seconds_label()
            self.start_run_timer()

    def start_run_timer(self):
        self.run_timer = Timer(1.0, self.reduce_run_remaining_seconds)
        self.run_timer.start()

    def reduce_run_remaining_seconds(self):
        self.remaining_secs_run -= 1
        self.update_run_remaining_seconds_label()
        if int(self.remaining_secs_run) > 0:
            self.start_run_timer()
        else:
            self.on_stop()
            self.update_run_remaining_seconds_label()
            self.set_run_remaining_seconds()
            self.start_pause_timer()

    def start_pause_timer(self):
        self.pause_timer = Timer(1.0, self.reduce_pause_remaining_seconds)
        self.pause_timer.start()

    def reduce_pause_remaining_seconds(self):
        self.remaining_secs_pause -= 1
        self.update_pause_remaining_seconds_label()
        if int(self.remaining_secs_pause) > 0:
            self.start_pause_timer()
        else:
            self.update_pause_remaining_seconds_label()
            self.set_pause_remaining_seconds()
            self.on_start()

    def on_stop(self):
        self.stop_pause_timer()
        self.stop_run_timer()
        self.parent.stop_drawing()

    def stop_pause_timer(self):
        if self.pause_timer is not None:
            self.pause_timer.cancel()
            self.set_pause_remaining_seconds()

    def stop_run_timer(self):
        if self.run_timer is not None:
            self.run_timer.cancel()
            self.set_run_remaining_seconds()

    def on_pause_seconds_changed(self):
        self.set_pause_remaining_seconds()
        self.update_pause_remaining_seconds_label()

    def on_pause_minutes_changed(self):
        self.set_pause_remaining_seconds()
        self.update_pause_remaining_seconds_label()

    def set_pause_remaining_seconds(self):
        self.remaining_secs_pause = self.minutes_to_seconds(self.interval_minutes_pause.get()) + int(
            self.interval_seconds_pause.get())

    def update_pause_remaining_seconds_label(self):
        self.remaining_secs_label_pause.configure(text=self.remaining_secs_pause)

    def on_run_seconds_changed(self):
        self.set_run_remaining_seconds()
        self.update_run_remaining_seconds_label()

    def on_run_minutes_changed(self):
        self.set_run_remaining_seconds()
        self.update_run_remaining_seconds_label()

    def set_run_remaining_seconds(self):
        self.remaining_secs_run = self.minutes_to_seconds(self.interval_minutes_run.get()) + int(
            self.interval_seconds_run.get())

    def update_run_remaining_seconds_label(self):
        self.remaining_secs_label_run.configure(text=self.remaining_secs_run)

    def minutes_to_seconds(self, value):
        return int(value) * MIN_TO_SEC

    def change_background_color(self, color):
        self.canvas.configure(background=color)
        self.parent.change_background_color_of_all_canvas(color, self.id_number)
        self.current_background_color = color

    def set_starting_position(self, event):
        self.starting_position = event.x / self.canvas.winfo_width(), event.y / self.canvas.winfo_height()
        self.on_generate()


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
        self.pygubu_builder.get_object(identifier + '_label', self.master)
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
        self.is_stopped = False
        self.now = 0

    def draw_predator(self, tab, all_tab, secondary, index):
        self.render(tab)
        self.render_copy_canvases(all_tab, index)
        self.render_copy_canvases(secondary, index)

    def render(self, tab):  # pragma: no cover
        tab.canvas.delete(tab.predator_draw_object)
        tab.predator_draw_object = self.render_predator(tab.canvas)

    def render_copy_canvases(self, copy_screen, index):  # pragma: no cover
        copy_screen.canvas[index].delete(copy_screen.predator_draw_object[index])
        copy_screen.predator_draw_object[index] = self.render_predator(copy_screen.canvas[index])

    def render_predator(self, canvas):  # pragma: no cover
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if self.is_stopped is False:
            self.now = int(time.time() * 1000)
        begin_x, begin_y, end_x, end_y = \
            self.calculate_coordinates(width, height, self.predator.get_current_diameter(self.now))

        return canvas.create_oval(begin_x, begin_y, end_x, end_y, fill=self.predator.color, outline=self.predator.color)

    def calculate_coordinates(self, width, height, current_diameter):  # pragma: no cover
        begin_x, begin_y = width * self.predator.get_starting_position()[0], \
                            height * self.predator.get_starting_position()[1]
        end_x, end_y = begin_x + current_diameter * width, begin_y + current_diameter * width

        pred_width, pred_height = end_x - begin_x, end_y - begin_y

        begin_x -= pred_width // 2
        begin_y -= pred_height // 2

        end_x -= pred_width // 2
        end_y -= pred_height // 2

        return begin_x, begin_y, end_x, end_y

    def stop(self):
        self.is_stopped = True

    def start(self):
        self.is_stopped = False


def get_startx_starty_horizontal(screen):
    return screen.winfo_reqwidth() * HORIZONTAL_X_MARGIN, \
           screen.winfo_reqheight() * HORIZONTAL_Y_MARGIN


def draw_horizontal_borders(height, screen, width):
    start_x, start_y = get_startx_starty_horizontal(screen)
    screen.create_line(start_x, start_y, width - start_x, start_y, fill="#CCCCCC")
    screen.create_line(start_x, height - start_y, width - start_x, height - start_y, fill="#CCCCCC")


def get_startx_starty_vertical(screen):
    return screen.winfo_reqwidth() * VERTICAL_X_MARGIN, \
           screen.winfo_reqheight() * VERTICAL_Y_MARGIN


def draw_vertical_borders(height, screen, width):
    start_x, start_y = get_startx_starty_vertical(screen)
    screen.create_line(start_x, start_y, start_x, height - start_y, fill="#CCCCCC")
    screen.create_line(width - start_x, start_y, width - start_x, height - start_y, fill="#CCCCCC")


def draw_outlines(screen):
    width, height = screen.winfo_reqwidth(), screen.winfo_reqheight()
    draw_horizontal_borders(height, screen, width)
    draw_vertical_borders(height, screen, width)


def draw_all_outlines(tab, all_tab, secondary, i):
    draw_outlines(tab.canvas)
    draw_outlines(all_tab.canvas[i])
    draw_outlines(secondary.canvas[i])
