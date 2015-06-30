from math import pi, cos, sin
import time
from tkinter import ALL

DEGREES_45 = pi/4.0


class TimeTracker(object):
    def __init__(self):
        self.starting_epoch = 0.0

    def start(self, epoch):
        self.starting_epoch = float(epoch)

    def get_delta(self, epoch):
        return float(epoch) / 1000. - self.starting_epoch / 1000.


class MovementVector(TimeTracker):

    def __init__(self, start, velocity):
        TimeTracker.__init__(self)
        self.starting_position = start
        self.angle = float(velocity[0])
        self.magnitude = float(velocity[1])

    def get_current_position(self, epoch):
        delta = self.get_delta(float(epoch))
        change_x = self.get_change_for_axis(cos, delta)
        change_y = self.get_change_for_axis(sin, delta)
        start_x, start_y = self.starting_position
        return start_x + change_x, start_y + change_y

    def get_change_for_axis(self, trigonometric_function, delta):
        delta_x = trigonometric_function(self.angle) * self.magnitude
        return delta_x * delta


class ScalingVector(TimeTracker):
    def __init__(self, target_diameter, velocity):
        TimeTracker.__init__(self)
        self.target_diameter = target_diameter
        self.velocity = velocity

    def get_current_diameter(self, epoch):
        return min(self.target_diameter, self.get_delta(float(epoch)) * self.velocity)

    def is_target_diameter_reached(self, epoch):
        return self.get_current_diameter(epoch) >= self.target_diameter


class PredatorFactory(object):
    def __init__(self):
        self.movement_velocity = (0, 0)
        self.starting_position = (0, 0)
        self.scaling_velocity = 0
        self.target_diameter = 0
        self.color = "#FFFFFF"

    def create(self):
        mv = MovementVector(self.starting_position, self.movement_velocity)
        sv = ScalingVector(self.target_diameter, self.scaling_velocity)
        return Predator(self.color, mv, sv)


class Predator(object):
    def __init__(self, color, mv, sv):
        self.color = color
        self.movement_vector = mv
        self.scaling_vector = sv

    def start_movement(self, starting_epoch):
        self.movement_vector.start(starting_epoch)

    def start_scaling(self, starting_epoch):
        self.scaling_vector.start(starting_epoch)

    def start_both(self, starting_epoch):
        self.start_movement(starting_epoch)
        self.start_scaling(starting_epoch)

    def reset_scaling(self, epoch):
        self.scaling_vector.start(epoch)

    def get_current_diameter(self, epoch):  # pragma: no cover
        if self.scaling_vector.is_target_diameter_reached(epoch):
            self.scaling_vector.start(int(time.time()*1000))
        return self.scaling_vector.get_current_diameter(epoch)

    def get_position(self):  # pragma: no cover
        return self.movement_vector.starting_position

    def set_scaling_velocity(self, value):  # pragma: no cover
        self.scaling_vector.velocity = value

    def set_target_diameter(self, value):  # pragma: no cover
        self.scaling_vector.target_diameter = value

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
            self.calculate_coordinates(width, height, self.get_current_diameter(now))

        return canvas.create_oval(begin_x, begin_y, end_x, end_y, fill=self.color, outline=self.color)

    def calculate_coordinates(self, height, width, current_diameter):  # pragma: no cover
        begin_x, begin_y = width*self.get_position()[0], height*self.get_position()[1]
        end_x, end_y = begin_x+current_diameter*width, begin_y+current_diameter*width

        pred_width, pred_height = end_x - begin_x, end_y - begin_y

        begin_x -= pred_width // 2
        begin_y -= pred_height // 2

        end_x -= pred_width // 2
        end_y -= pred_height // 2
        return begin_x, begin_y, end_x, end_y
