import matplotlib.pyplot as plt
import numpy as np


class PixelPicker:
    # When plotting in matplotlib the OFFSET is used with image extent
    OFFSET = 0.5
    MARKERSIZE = 1

    def __init__(self, figure, lines, radius, pick_button, erase_button, reset_button, is_interpolation_used):
        self.xys = set()
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

        # Callbacks
        self.cid = figure.canvas.mpl_connect('button_press_event', self._on_click)
        self.cidmotion = figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.cidrealease = figure.canvas.mpl_connect('button_release_event', self._on_release)
        self.axs[0].callbacks.connect('xlim_changed', self._update_marker_size)
        self.axs[0].callbacks.connect('ylim_changed', self._update_marker_size)

    def _update_marker_size(self, axes=None):
        ppd = 72. / self.axs[0].figure.dpi
        trans = self.axs[0].transData.transform
        for line in self.lines:
            size = ((trans((1, self.MARKERSIZE)) - trans((0, 0))) * ppd)[1]
            line.set_markersize(abs(size))
        self._render()

    def _on_click(self, event):
        # print('click', event)
        if self._valid_pick_event(event):
            # Hand mouse cursor = 0, arrow = 1, cross = 2
            self.figure.canvas.toolbar.set_cursor(0)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))
            self._add_rectangle(event)
        elif self._valid_erase_event(event):
            # Hand mouse cursor = 0, arrow = 1, cross = 2
            self.figure.canvas.toolbar.set_cursor(0)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))
            self._remove_rectangle(event)
        elif self._valid_reset_event(event):
            self.xys = set()
            self._draw_picked_pixels()

    def _on_motion(self, event):
        # print('motion', event)
        if self._valid_pick_event(event):
            self._add_rectangle(event)
            self.previous_xy = (int(round(event.xdata)), int(round(event.ydata)))
        elif self._valid_erase_event(event):
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
                and self.figure.canvas.manager.toolbar._active is None
                # Cursor inside image
                and any([axes.get_images()[0].contains(event)[0] for axes in self.axs])
        )

    def _valid_erase_event(self, event):
        return (
                event.inaxes in self.axs
                # Right button pressed
                and event.button == self.erase_button
                # No tool is active
                and self.figure.canvas.manager.toolbar._active is None
                # Cursor inside image
                and any([axes.get_images()[0].contains(event)[0] for axes in self.axs])
        )

    def _valid_reset_event(self, event):
        return (
                event.inaxes in self.axs
                # Right button pressed
                and event.button == self.reset_button
                # No tool is active
                and self.figure.canvas.manager.toolbar._active is None
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
        if self.is_interpolation_used:
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
        if len(self.xys) > 1:
            xs, ys = zip(*self.xys)
        else:
            xs = ys = []
        for line in self.lines:
            line.set_data(xs, ys)

        self._render()

    def _render(self):
        self.figure.canvas.draw_idle()

    def get_pixels(self):
        return list(self.xys)

    def clear(self):
        for line in self.lines:
            line.set_data([], [])
        self._render()


def pick_pixels(class_num=0, radius=8, color=(1, 0, 0, 0.5),
                pick_button=1, erase_button=3, reset_button=2,
                is_interpolation_used=True):
    """

    :param class_num: Number of the class
    :param radius: Radius of the drawing circle
    :param color: Color of the painted pixels
    :param pick_button: 1 = left click, 2 = middle click, 3 = right click, None = no button
    :param erase_button: 1 = left click, 2 = middle click, 3 = right click, None = no button
    :param reset_button: 1 = left click, 2 = middle click, 3 = right click, None = no button
    :param is_interpolation_used: True = Interpolates points in between when moving mouse too fast, False = No interpolation
    :return: Class number and after that pixel x and y coordinates as tuples inside a list
    """
    fig = list(map(plt.figure, plt.get_fignums()))[0]
    lines = []
    continue_picking = True

    for axes in fig.get_axes():
        line, = axes.plot([], [], linestyle="none", marker='s', markersize=1, color=color)
        lines.append(line)

    picker = PixelPicker(fig, lines, radius, pick_button, erase_button, reset_button, is_interpolation_used)
    while continue_picking:
        result = input("Press enter to stop picking pixels or choose a pixel radius: ")
        if result == "":
            continue_picking  = False
            break
        elif result.isdigit():
            picker.radius = int(result)
        else:
            print("Unknown command")
    #input("Press enter to stop picking pixels ")
    pixels = [class_num] + picker.get_pixels()
    picker.clear()
    return pixels if len(pixels) > 1 else []


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
