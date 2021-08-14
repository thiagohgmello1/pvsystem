import numpy as np


class Camera:
    def __init__(self, theta_x=None, theta_y=None, film_size=(0, 0), stated_focal_length=None):
        self.theta_x = theta_x
        self.theta_y = theta_y
        self.dx = film_size[0]
        self.dy = film_size[1]
        self.F = stated_focal_length
        self.angle_of_view_calculator()

    def angle_of_view_calculator(self):
        if (self.theta_x and self.theta_y) is None:
            self.theta_x = np.rad2deg(2 * np.arctan(self.dx / (2 * self.F)))
            self.theta_y = np.rad2deg(2 * np.arctan(self.dy / (2 * self.F)))