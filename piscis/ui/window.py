#-*- encoding: utf-8 -*-

from os import path
from tkinter import messagebox, Frame, Label, Button, Canvas
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo
from pygubu import Builder, TkApplication

VERTICAL_Y_MARGIN = 0.15

VERTICAL_X_MARGIN = 0.014

HORIZONTAL_Y_MARGIN = 0.044

HORIZONTAL_X_MARGIN = 0.09

TITLE_FONT = {"Helvetica", 18, "bold"}

class MainWindow(TkApplication):
    def _create_ui(self):
        self.builder = Builder()
        self.builder.add_from_file(path.join(".", "forms", "window.ui"))

        self.main_window = self.setup_window()
        self.main_menu = self.setup_menu()
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
        self.setup_screen_one(all_screens)
        self.setup_screen_two(all_screens)
        self.setup_screen_three(all_screens)
        self.setup_screen_four(all_screens)

    def setup_screen_one(self, all_screens):
        screen_one = self.builder.get_object('screenone_text', self.master)
        return Screen(screen_one, all_screens.screen_one)

    def setup_screen_two(self, all_screens):
        screen_two = self.builder.get_object('screentwo_text', self.master)
        return Screen(screen_two, all_screens.screen_two)

    def setup_screen_three(self, all_screens):
        screen_three = self.builder.get_object('screenthree_text', self.master)
        return Screen(screen_three, all_screens.screen_three)

    def setup_screen_four(self, all_screens):
        screen_four = self.builder.get_object('screenfour_text', self.master)
        return Screen(screen_four, all_screens.screen_four)

    def setup_all_screens(self):
        all_screens = self.builder.get_object('allscreens_text', self.master)
        return AllScreens(all_screens)

    def on_about(self):
        showinfo("Piscis", "Piscis - Pre-Alpha\nContact: soojin.ryu@mpimf-heidelberg.mpg.de")

    def on_exit(self):
        self.master.quit()


class AllScreens(object):
    def __init__(self, root):
        self.root = root
        self.builder = Builder()
        self.builder.add_from_file(path.join(".", "forms", "all_screens.ui"))

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

    def __init__(self, root, parent_canvas):
        self.root = root
        self.parent_canvas = parent_canvas
        self.canvas = None
        self.builder = Builder()
        self.builder.add_from_file(path.join(".", "forms", "screen_one.ui"))
        self.setup_screen()
        self.builder.connect_callbacks(self)

    def setup_screen(self):
        self.setup_canvas()
        self.setup_fishbox()
        self.setup_scale_slider()
        self.setup_speed_slider()
        self.setup_buttons()

    def setup_canvas(self):
        self.canvas = self.builder.get_object('canvas', self.root)
        self.change_canvas_background(self.CANVAS_DEFAULT_BACKGROUND)

    def change_canvas_background(self, value):
        self.canvas.configure(background=value)
        self.parent_canvas.configure(background=value)

    def setup_fishbox(self):
        # noinspection PyTypeChecker
        self.setup_fishbox_canvas(self.canvas)
        self.setup_fishbox_canvas(self.parent_canvas)

    def setup_fishbox_canvas(self, screen):
        width, height = screen.winfo_reqwidth(), screen.winfo_reqheight()
        self.draw_horizontal_borders(height, screen, width)
        self.draw_vertical_borders(height, screen, width)

    def draw_horizontal_borders(self, height, screen, width):
        start_x, start_y = self.get_startx_starty_horizontal(screen)
        screen.create_line(start_x, start_y, width - start_x, start_y, fill="#CCCCCC")
        screen.create_line(start_x, height - start_y, width - start_x, height - start_y, fill="#CCCCCC")

    def get_startx_starty_horizontal(self, screen):
        return screen.winfo_reqwidth()* HORIZONTAL_X_MARGIN, \
               screen.winfo_reqheight()* HORIZONTAL_Y_MARGIN

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
        self.builder.get_object('stimuli', self.root)

    def on_background(self):
        new_bg_color = askcolor(color=self.CANVAS_DEFAULT_BACKGROUND, title="Change Background-Color")[1]
        self.change_canvas_background(new_bg_color)

    def on_stimuli(self):
        askcolor(color="#FFFFFF", title="Change Stimuli-Color")

    def on_speed_slider(self, value):
        print(str(value))

    def on_scale_slider(self, value):
        print(str(value))