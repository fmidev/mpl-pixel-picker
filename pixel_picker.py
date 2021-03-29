import matplotlib.pyplot as plt
import numpy as np
import importlib

#############################################################
## PixelPicker
## A tool for picking pixels from maptplotlib plotted images
#############################################################
## Author: Joona Laine, Sanna Hautala, Spatineo Oy
## Copyright: Copyright 2019, PixelPicker
#############################################################

__author__ = 'Joona Laine, Sanna Hautala, Spatineo Oy'
__copyright__ = 'Copyright 2019, PixelPicker'

class PixelPicker:
    """PixelPicker for picking pixels from matplotlib plotted images"""
    # When plotting in matplotlib the OFFSET is used with image extent
    OFFSET = 0.5
    MARKERSIZE = 1

    def __init__(self, figure, lines, radius, pick_button, erase_button, reset_button, is_interpolation_used, xys):
        self.xys = xys
        self.previous_xy = None
        self.figure = figure
        self.axs = figure.get_axes()
        self.pick_button = pick_button
        self.erase_button = erase_button
        self.reset_button = reset_button
        self.is_interpolation_used = is_interpolation_used
        self.radius = radius
        self.x_min, self.x_max, self.y_max, self.y_min = [int(val + self.OFFSET) for val in
                                                          self.axs[0].get_images()[0].get_extent()]

        # Draw must be called in order to update the marker size properly
        self._render()
        self.lines = lines
        self._update_marker_size()
        self._draw_picked_pixels()

        # Callbacks
        self.cid = figure.canvas.mpl_connect('button_press_event', self._on_click)
        self.cidmotion = figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.cidrealease = figure.canvas.mpl_connect('button_release_event', self._on_release)
        self.axs[0].callbacks.connect('xlim_changed', self._update_marker_size)
        self.axs[0].callbacks.connect('ylim_changed', self._update_marker_size)

    def get_pixels(self):
        """Returns list of coordinate tuples"""
        return list(self.xys)

    def reset_pixels(self):
        """Reset picked pixels"""
        self.xys = set()
        self._draw_picked_pixels()

    def clear(self):
        """Clears picked pixels"""
        for line in self.lines:
            line.set_data([], [])
        self._render()

    def _update_marker_size(self, axes=None):
        ppd = 72. / self.axs[0].figure.dpi
        trans = self.axs[0].transData.transform
        for line in self.lines:
            size = ((trans((1, self.MARKERSIZE)) - trans((0, 0))) * ppd)[1]
            line.set_markersize(abs(size))
        self._render()

    def _on_click(self, event):
        if self._valid_event(event, self.pick_button):
            # Hand mouse cursor = 0, arrow = 1, cross = 2
            self.figure.canvas.toolbar.set_cursor(0)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))
            self._add_rectangle(event)
        elif self._valid_event(event, self.erase_button):
            # Hand mouse cursor = 0, arrow = 1, cross = 2
            self.figure.canvas.toolbar.set_cursor(0)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))
            self._remove_rectangle(event)
        elif self._valid_event(event, self.reset_button):
            self.reset_pixels()

    def _on_motion(self, event):
        if self._valid_event(event, self.pick_button):
            self._add_rectangle(event)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))
        elif self._valid_event(event, self.erase_button):
            self._remove_rectangle(event)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))

    def _on_release(self, event):
        self.previous_xy = None
        if self._valid_event(event, self.pick_button):
            self.figure.canvas.toolbar.set_cursor(1)
        if self._valid_event(event, self.erase_button):
            self.figure.canvas.toolbar.set_cursor(1)

    def _valid_event(self, event, button):
        return (
                event.inaxes in self.axs
                # Right button pressed
                and event.button == button
                # No tool is active
                and self.figure.canvas.manager.toolbar.mode == ''
                # Cursor inside image
                and any([axes.get_images()[0].contains(event)[0] for axes in self.axs])
        )

    @staticmethod
    def _get_interpolated_xy(xy, previous_xy):
        interpolated_xy = set()
        is_not_inverted = abs(xy[0] - previous_xy[0]) >= abs(xy[1] - previous_xy[1])
        xy = xy if is_not_inverted else (xy[1], xy[0])
        previous_xy = previous_xy if is_not_inverted else (previous_xy[1], previous_xy[0])
        dx = xy[0] - previous_xy[0]
        dy = xy[1] - previous_xy[1]
        for x in range(previous_xy[0], xy[0], -1 if previous_xy[0] > xy[0] else 1):
            y = previous_xy[1] + dy * (x - previous_xy[0]) / dx
            interpolated_xy.add((int(round(x if is_not_inverted else y)), int(round(y if is_not_inverted else x))))
        return interpolated_xy

    def _get_xys_from_event(self, event):
        xys = set()
        xy = (int(round(event.xdata)), int(round(event.ydata)))
        xys.add(xy)
        if self.is_interpolation_used and self.previous_xy is not None:
            xys.update(self._get_interpolated_xy(xy, self.previous_xy))

        rounding_xys = set()
        if self.radius > 0:
            for xy in xys:
                xo, yo = xy
                for x in range(max(xo - self.radius, self.x_min), min(xo + self.radius + 1, self.x_max)):
                    for y in range(max(yo - self.radius, self.y_min), min(yo + self.radius + 1, self.y_max)):
                        # In circle
                        if (x - xo) ** 2 + (y - yo) ** 2 <= self.radius ** 2:
                            rounding_xys.add((x, y))

        return xys.union(rounding_xys)

    def _add_rectangle(self, event):
        xys_to_add = self._get_xys_from_event(event).difference(self.xys)
        if len(xys_to_add) > 0:
            self.xys.update(xys_to_add)
            self._draw_picked_pixels()

    def _remove_rectangle(self, event):
        xys_to_remove = self._get_xys_from_event(event).intersection(self.xys)
        if len(xys_to_remove) > 0:
            self.xys = self.xys.difference(xys_to_remove)
            self._draw_picked_pixels()

    def _draw_picked_pixels(self):
        if len(self.xys) > 0:
            xs, ys = zip(*self.xys)
        else:
            xs = ys = []
        for line in self.lines:
            line.set_data(xs, ys)
        self._render()

    def _render(self):
        self.figure.canvas.draw_idle()


def gui(picker):
    """Graphical ui for pixel picker"""
    import tkinter as tk

    gui_window = tk.Tk()
    gui_window.title("Pixel picker")
    tk.Label(gui_window, text="Radius").grid(row=0, pady=4)
    e1 = tk.Entry(gui_window)
    e1.insert(10, picker.radius)
    e1.grid(row=0, column=1)

    def change_radius():
        picker.radius = int(e1.get())

    def reset_xys():
        picker.reset_pixels()

    tk.Button(gui_window,
        text='Set Radius',
        command=change_radius).grid(row=2, column=0, sticky=tk.W, pady=4, padx=4)
    tk.Button(gui_window,
        text='Reset pixels',
        command=reset_xys).grid(row=2, column=2, sticky=tk.W, pady=4, padx=4)
    tk.Button(gui_window,
        text='Get pixels',
        command=gui_window.quit).grid(row=2, column=3, sticky=tk.W, pady=4, padx=4)
    gui_window.mainloop()


def ui(picker):
    continue_picking = True
    while continue_picking:
        result = input("Press enter to stop picking pixels, r to reset pixels or choose a pixel radius: ")
        if result == "":
            continue_picking  = False
        elif result == "r":
            picker.reset_pixels()
        elif result.isdigit():
            picker.radius = int(result)
        else:
            print("Unknown command")


def pick_pixels(class_num=0, radius=8, color=(1, 0, 0, 0.5),
                pick_button=1, erase_button=3, reset_button=2,
                is_interpolation_used=True, picked_coordinates=tuple(), use_gui=False):
    """
    Helper function to start picking pixels

    :param class_num: Number of the class
    :param radius: Radius of the drawing circle (0 = 1 pixel)
    :param color: Color of the painted pixels
    :param pick_button: 1 = left click, 2 = middle click, 3 = right click, None = no button
    :param erase_button: 1 = left click, 2 = middle click, 3 = right click, None = no button
    :param reset_button: 1 = left click, 2 = middle click, 3 = right click, None = no button
    :param is_interpolation_used: True = Interpolates points in between when moving mouse too fast, False = No interpolation
    :param picked_coordinates: Already picked coordinates. Format: Class number and after that pixel x and y coordinates
    as tuples inside a list or tuple
    :param use_gui: True = Use graphical ui if tkinter is installed, False = use command line option
    :return: Class number and after that pixel x and y coordinates as tuples inside a list
    """
    fig = list(map(plt.figure, plt.get_fignums()))[0]
    lines = []

    # The first value of the picked_coordinates is probably a class_num, let's ommit that
    xys = set(picked_coordinates[1:])

    for axes in fig.get_axes():
        line, = axes.plot([], [], linestyle="none", marker='s', markersize=1, color=color)
        lines.append(line)

    picker = PixelPicker(fig, lines, radius, pick_button, erase_button, reset_button, is_interpolation_used, xys)

    if use_gui and importlib.util.find_spec("tkinter"):
        gui(picker)
    else:
        if not importlib.util.find_spec("tkinter"):
            print("Tkinter not installed. Using command line interface.")
        ui(picker)

    pixels = [class_num] + picker.get_pixels()
    picker.clear()
    return pixels if len(pixels) > 1 else []


def generate_random_image(loc, title, h=600, w=600, old_ax=None):
    """Returns random image"""
    img = (np.random.standard_normal([h, w, 3]) * 255).astype(np.uint8)
    ax = plt.subplot(loc) if old_ax is None else plt.subplot(loc, sharex=old_ax, sharey=old_ax)
    ax.set_adjustable('box')
    plt.title(title)
    plt.axis('off')
    plt.imshow(img)
    return ax


def generate_test_figure():
    """Generates test figures using matplotlib and random generated images"""
    plt.figure(1, figsize=(8, 10))
    plt.clf()
    plt.ion()
    ax = generate_random_image(211, "Test 1")
    generate_random_image(212, "Test 2", old_ax=ax)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    generate_test_figure()
    pixels = pick_pixels()
    print("Number of pixels picked:", len(pixels))
