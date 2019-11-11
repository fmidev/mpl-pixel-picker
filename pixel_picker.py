import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

# When plotting in matplotlib the upper left corner has the values of:
Y_OFFSET = - 0.5
X_OFFSET = -0.5


class PixelPicker:
    def __init__(self, figure, rect_colls, lines, markersize, pick_button, erase_button, is_interpolation_used,
                 use_rectangles=False):
        self.xys = dict()
        self.previous_xy = None
        self.rects = []
        self.figure = figure
        self.axs = figure.get_axes()

        self.use_rectangles = use_rectangles
        self._render()
        self.size_data = markersize
        self.size = markersize
        self.lines = lines
        self._update_marker_size()

        self.rect_colls = rect_colls
        self.pick_button = pick_button
        self.erase_button = erase_button
        self.is_interpolation_used = is_interpolation_used
        self.cid = figure.canvas.mpl_connect('button_press_event', self._on_click)
        self.cidmotion = figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.cidrealease = figure.canvas.mpl_connect('button_release_event', self._on_release)
        self.axs[0].callbacks.connect('xlim_changed', self._update_marker_size)
        self.axs[0].callbacks.connect('ylim_changed', self._update_marker_size)

    def _update_marker_size(self, axes=None):
        ppd = 72. / self.axs[0].figure.dpi
        trans = self.axs[0].transData.transform
        for line in self.lines:
            size = ((trans((1, self.size_data)) - trans((0, 0))) * ppd)[1]
            line.set_markersize(abs(size))
        self._render()

    def _on_click(self, event):
        # print('click', event)
        if self._valid_pick_event(event):
            # Hand mouse cursor = 0, arrow = 1, cross = 2
            self.figure.canvas.toolbar.set_cursor(0)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))
            if self.use_rectangles:
                self._add_rectangle2(event)
            else:
                self._add_rectangle(event)
        elif self._valid_erase_event(event):
            # Hand mouse cursor = 0, arrow = 1, cross = 2
            self.figure.canvas.toolbar.set_cursor(0)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))
            if self.use_rectangles:
                self._remove_rectangle2(event)
            else:
                self._remove_rectangle(event)

    def _on_motion(self, event):
        # print('motion', event)
        if self._valid_pick_event(event):
            if self.use_rectangles:
                self._add_rectangle2(event)
            else:
                self._add_rectangle(event)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))
        elif self._valid_erase_event(event):
            if self.use_rectangles:
                self._remove_rectangle2(event)
            else:
                self._remove_rectangle(event)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))

    def _on_release(self, event):
        # print('relese', event)
        if self._valid_pick_event(event):
            self.figure.canvas.toolbar.set_cursor(1)
        if self._valid_erase_event(event):
            self.figure.canvas.toolbar.set_cursor(1)

    def _valid_pick_event(self, event):
        return (
                event.inaxes in self.axs
                # Right button pressed
                and event.button == self.pick_button
                # No tool is active
                and self.figure.canvas.manager.toolbar._active == None
                # Cursor inside image
                and any([axes.get_images()[0].contains(event)[0] for axes in self.axs])
        )

    def _valid_erase_event(self, event):
        return (
                event.inaxes in self.axs
                # Right button pressed
                and event.button == self.erase_button
                # No tool is active
                and self.figure.canvas.manager.toolbar._active == None
                # Cursor inside image
                and any([axes.get_images()[0].contains(event)[0] for axes in self.axs])
        )

    def get_interpolated_xy(self, xy, previous_xy):
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
        if self.is_interpolation_used:
            xys.update(self.get_interpolated_xy(xy, self.previous_xy))
        return xys

    def _add_rectangle(self, event):
        xys_to_add = self._get_xys_from_event(event).difference(self.xys.keys())

        if len(xys_to_add) > 0:
            for xy in xys_to_add:
                self.xys[xy] = Rectangle((xy[0] + X_OFFSET, xy[1] + Y_OFFSET), 1, 1)
            for line in self.lines:
                line.set_data([xy[0] for xy in self.xys.keys()], [xy[1] for xy in self.xys.keys()])
            self._render()

    def _add_rectangle2(self, event):
        xys_to_add = self._get_xys_from_event(event).difference(self.xys.keys())

        if len(xys_to_add) > 0:
            for xy in xys_to_add:
                self.xys[xy] = Rectangle((xy[0] + X_OFFSET, xy[1] + Y_OFFSET), 1, 1)
            rects = self.xys.values()
            for rect_coll in self.rect_colls:
                rect_coll.set_paths(rects)
            self._render()

    def _remove_rectangle(self, event):
        xys_to_remove = self._get_xys_from_event(event).intersection(self.xys.keys())
        if len(xys_to_remove) > 0:
            for xy in xys_to_remove:
                self.xys.pop(xy, None)
            for line in self.lines:
                line.set_data([xy[0] for xy in self.xys.keys()], [xy[1] for xy in self.xys.keys()])
            self._render()

    def _remove_rectangle2(self, event):
        xys_to_remove = self._get_xys_from_event(event).intersection(self.xys.keys())

        if len(xys_to_remove) > 0:
            for xy in xys_to_remove:
                self.xys.pop(xy, None)
            rects = self.xys.values()
            for rect_coll in self.rect_colls:
                rect_coll.set_paths(rects)
            self._render()

    def _render(self):
        self.figure.canvas.draw_idle()

    def get_pixels(self):
        return list(self.xys.keys())

    def clear(self):
        for rect_coll in self.rect_colls:
            rect_coll.set_paths([])
        for line in self.lines:
            line.set_data([], [])
        self._render()


def pick_pixels(class_num=0, color=(1, 0, 0, 0.7), pick_button=1, erase_button=3, is_interpolation_used=True,
                markersize=1):
    """

    :param class_num: Number of the class
    :param color: Color of the painted pixels
    :param pick_button: 1 = left click, 3 = right click
    :param erase_button: 1 = left click, 3 = right click
    :param is_interpolation_used: True = Interpolates points in between when moving mouse too fast, False = No interpolation
    :return: Class number and after that pixel x and y coordinates as tuples inside a list
    """
    fig = list(map(plt.figure, plt.get_fignums()))[0]
    rect_colls = []
    lines = []
    for axes in fig.get_axes():
        line, = axes.plot([], [], linestyle="none", marker='s', markersize=markersize, color=color)
        lines.append(line)
        rectangle_collection = PatchCollection([], facecolors=color, edgecolors=color)
        axes.add_collection(rectangle_collection)
        rect_colls.append(rectangle_collection)

    picker = PixelPicker(fig, rect_colls, lines, markersize, pick_button, erase_button, is_interpolation_used,
                         use_rectangles=False)
    input("Press enter to stop picking pixels")
    pixels = [class_num] + picker.get_pixels()
    picker.clear()
    return pixels


def generate_random_image(loc, title, h=600, w=600, old_ax=None):
    img = (np.random.standard_normal([h, w, 3]) * 255).astype(np.uint8)
    ax = plt.subplot(loc) if old_ax is None else plt.subplot(loc, sharex=old_ax, sharey=old_ax)
    ax.set_adjustable('box')
    plt.title(title)
    plt.axis('off')
    plt.imshow(img)
    return ax


def generate_test_figure():
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
