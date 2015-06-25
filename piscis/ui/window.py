#-*- encoding: utf-8 -*-

from os import path
import random
from tkinter import messagebox, Frame, Label, Button, Canvas, Toplevel, Tk
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo
from tkinter.ttk import Style
from pygubu import Builder, TkApplication

VERTICAL_Y_MARGIN = 0.15

VERTICAL_X_MARGIN = 0.014

HORIZONTAL_Y_MARGIN = 0.044

HORIZONTAL_X_MARGIN = 0.09

TITLE_FONT = {"Helvetica", 18, "bold"}

SCRIPT_DIR = path.dirname(path.abspath(__file__))

class MainWindow(TkApplication):
    def _create_ui(self):
        self.builder = Builder()
        file = path.join(SCRIPT_DIR, "forms", "window.ui")
        self.builder.add_from_file(file)

        self.main_window = self.setup_window()
        self.main_menu = self.setup_menu()
        self.second_monitor = self.setup_second_monitor()
        self.setup_screens()
        
        self.builder.connect_callbacks(self)

    def setup_window(self):
        self.set_title("Piscis - Pre-Alpha")
        return self.builder.get_object('main_window', self.master)

    def setup_menu(self):
        main_menu = self.builder.get_object('main_menu', self.master)
        self.set_menu(main_menu)
        return main_menu

    def setup_screens(self):
        all_screens = self.setup_all_screens()
        self.setup_screen_one(all_screens, self.second_monitor)
        self.setup_screen_two(all_screens, self.second_monitor)
        self.setup_screen_three(all_screens, self.second_monitor)
        self.setup_screen_four(all_screens, self.second_monitor)

    def setup_screen_one(self, all_screens, window):
        screen_one = self.builder.get_object('screenone_text', self.master)
        return Screen(screen_one, all_screens.screen_one, window.screen_one)

    def setup_screen_two(self, all_screens, window):
        screen_two = self.builder.get_object('screentwo_text', self.master)
        return Screen(screen_two, all_screens.screen_two, window.screen_two)

    def setup_screen_three(self, all_screens, window):
        screen_three = self.builder.get_object('screenthree_text', self.master)
        return Screen(screen_three, all_screens.screen_three, window.screen_three)

    def setup_screen_four(self, all_screens, window):
        screen_four = self.builder.get_object('screenfour_text', self.master)
        return Screen(screen_four, all_screens.screen_four, window.screen_four)

    def setup_all_screens(self):
        all_screens = self.builder.get_object('allscreens_text', self.master)
        return AllScreens(all_screens)

    def on_about(self):
        showinfo("Piscis", "Piscis - Pre-Alpha\nContact: soojin.ryu@mpimf-heidelberg.mpg.de")

    def on_exit(self):
        self.master.quit()

    def on_fullscreen(self):
        self.second_monitor.set_fullscreen()

    def change_fullscreen_bg(self):
        new_color = askcolor(color=self.second_monitor.bg_color, title="Change Background-Color")[1]
        self.second_monitor.change_background_color(new_color)

    def setup_second_monitor(self):
        return SecondScreen(Toplevel())

class SecondScreen(object):
    def __init__(self, root):
        self.root = root
        self.builder = Builder()
        self.builder.add_from_file(path.join(SCRIPT_DIR, "forms", "second_screen.ui"))

        self.bg_color = '#3F8080'

        self.style = Style()
        self.change_background_color(self.bg_color)
        self.main_frame = self.builder.get_object('main_frame', self.root)

        self.screen_one = self.builder.get_object('screen_one', self.root)
        self.screen_two = self.builder.get_object('screen_two', self.root)
        self.screen_three = self.builder.get_object('screen_three', self.root)
        self.screen_four = self.builder.get_object('screen_four', self.root)

    def set_fullscreen(self):
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.overrideredirect(1)
        self.root.geometry("%dx%d+0+0" % (w, h))

    def change_background_color(self, color):
        self.bg_color = color
        self.style.configure('TFrame', background=color)

class AllScreens(object):
    def __init__(self, root):
        self.root = root
        self.builder = Builder()
        self.builder.add_from_file(path.join(SCRIPT_DIR, "forms", "all_screens.ui"))
        self.screen_one = self.builder.get_object('screen_one', self.root)
        self.screen_two = self.builder.get_object('screen_two', self.root)
        self.screen_three = self.builder.get_object('screen_three', self.root)
        self.screen_four = self.builder.get_object('screen_four', self.root)

        self.builder.get_object('screen_one_text', self.root)
        self.builder.get_object('screen_two_text', self.root)
        self.builder.get_object('screen_three_text', self.root)
        self.builder.get_object('screen_four_text', self.root)


class Screen(object):
    CANVAS_DEFAULT_BACKGROUND = "#3F8080"
    PREDATOR_COLOR = "#FFFFFF"

    def __init__(self, root, parent_canvas, window_canvas):
        self.root = root

        self.parent_canvas = parent_canvas
        self.window_canvas = window_canvas
        self.canvas = None

        self.predator_canvas = None
        self.predator_parent_canvas = None
        self.predator_window_canvas = None

        self.speed_slider_value = 0
        self.scale_slider_value = 0

        self.builder = Builder()
        self.builder.add_from_file(path.join(SCRIPT_DIR, "forms", "screen_one.ui"))
        self.setup_screen()
        self.builder.connect_callbacks(self)

        self.root.after(40, self.update)

    def setup_screen(self):
        self.setup_canvas()
        self.setup_fishbox()
        self.setup_scale_slider()
        self.setup_speed_slider()
        self.setup_buttons()

    def setup_canvas(self):
        self.canvas = self.builder.get_object('canvas', self.root)

    def change_canvas_background(self, value):
        self.canvas.configure(background=value)
        self.parent_canvas.configure(background=value)
        self.window_canvas.configure(background=value)

    def setup_fishbox_canvas(self, screen):
        width, height = screen.winfo_reqwidth(), screen.winfo_reqheight()
        self.draw_horizontal_borders(height, screen, width)
        self.draw_vertical_borders(height, screen, width)

    def setup_fishbox(self):
        # noinspection PyTypeChecker
        self.setup_fishbox_canvas(self.canvas)
        self.setup_fishbox_canvas(self.parent_canvas)
        self.setup_fishbox_canvas(self.window_canvas)

    def draw_horizontal_borders(self, height, screen, width):
        start_x, start_y = self.get_startx_starty_horizontal(screen)
        self.change_canvas_background(self.CANVAS_DEFAULT_BACKGROUND)
        screen.create_line(start_x, start_y, width - start_x, start_y, fill="#CCCCCC")
        screen.create_line(start_x, height - start_y, width - start_x, height - start_y, fill="#CCCCCC")

    def get_startx_starty_horizontal(self, screen):
        return screen.winfo_reqwidth()*HORIZONTAL_X_MARGIN, \
               screen.winfo_reqheight()*HORIZONTAL_Y_MARGIN

    def draw_vertical_borders(self, height, screen, width):
        start_x, start_y = self.get_startx_starty_vertical(screen)
        screen.create_line(start_x, start_y, start_x, height - start_y, fill="#CCCCCC")
        screen.create_line(width - start_x, start_y, width - start_x, height - start_y, fill="#CCCCCC")

    def get_startx_starty_vertical(self, screen):
        return screen.winfo_reqwidth()*VERTICAL_X_MARGIN, \
               screen.winfo_reqheight()*VERTICAL_Y_MARGIN

    def setup_scale_slider(self):
        self.builder.get_object('scale_label', self.root)
        self.builder.get_object('scale_slider', self.root)

    def setup_speed_slider(self):
        self.builder.get_object('speed_label', self.root)
        self.builder.get_object('speed_slider', self.root)

    def setup_buttons(self):
        self.builder.get_object('background', self.root)
        self.builder.get_object('stimuli_color', self.root)
        self.builder.get_object('generate', self.root)

    def on_background(self):
        new_bg_color = askcolor(color=self.CANVAS_DEFAULT_BACKGROUND, title="Change Background-Color")[1]
        self.change_canvas_background(new_bg_color)

    def on_stimuli_color(self):
        self.PREDATOR_COLOR = askcolor(color=self.PREDATOR_COLOR, title="Change Stimuli-Color")[1]

    def on_speed_slider(self, value):
        self.speed_slider_value = float(value)

    def on_scale_slider(self, value):
        self.scale_slider_value = float(value)

    def on_generate(self):
        self.reset_predators()
        self.create_predators()

    def reset_predators(self):
        self.canvas.delete(self.predator_canvas)
        self.parent_canvas.delete(self.predator_parent_canvas)
        self.window_canvas.delete(self.predator_window_canvas)

    def create_predators(self):
        x, y = random.random(), random.random()

        self.predator_canvas = self.draw_predator(x, y, self.canvas)
        self.predator_parent_canvas = self.draw_predator(x, y, self.parent_canvas)
        self.predator_window_canvas = self.draw_predator(x, y, self.window_canvas)

    def draw_predator(self, x, y, canvas):
        width, height = canvas.winfo_width(), canvas.winfo_height()
        begin_x, begin_y, end_x, end_y = self.calculate_coordinates(height, width, x, y)

        return canvas.create_oval(begin_x, begin_y, end_x, end_y, fill=self.PREDATOR_COLOR,
                                  outline=self.PREDATOR_COLOR)

    def calculate_coordinates(self, height, width, x, y):
        begin_x, begin_y = x * width, y * height
        end_x, end_y = x * width + width * self.scale_slider_value, y * height + width * self.scale_slider_value
        pred_width, pred_height = end_x - begin_x, end_y - begin_y

        begin_x -= pred_width // 2
        begin_y -= pred_height // 2

        end_x -= pred_width // 2
        end_y -= pred_height // 2
        return begin_x, begin_y, end_x, end_y

    def update(self):
        pass
