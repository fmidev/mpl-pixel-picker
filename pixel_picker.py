import matplotlib.pyplot as plt
import numpy as np


class PixelPicker:
    def __init__(self, line, ax, mouse_button):
        self.line = line
        self.ax = ax
        self.mouse_button = mouse_button
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)
        self.cidmotion = self.line.figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        ax.callbacks.connect('xlim_changed', self._on_xlims_change)
        ax.callbacks.connect('ylim_changed', self._on_ylims_change)

    def __call__(self, event):
        # print('click', event)
        if event.inaxes != self.line.axes or event.button != self.mouse_button: return
        self._draw_dot(event)

    def _on_xlims_change(self, axes):
        print("x_lim changed", self.ax.get_xlim())

    def _on_ylims_change(self, axes):
        print("y_lim canhed", self.ax.get_ylim())

    def _on_motion(self, event):
        # print('motion', event)
        if event.inaxes != self.line.axes or event.button != self.mouse_button: return
        self._draw_dot(event)

    def _draw_dot(self, event):
        self.xs.append(int(event.xdata))
        self.ys.append(int(event.ydata))
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()

    def get_pixels(self):
        return list(set([(self.xs[i], self.ys[i]) for i in range(len(self.xs))]))


def pick_pixels(class_num=0, color=(1, 0, 0, 0.8), marker="s", mouse_button=3):
    """

    :param class_num: Number of the class
    :param color: Color of the painted pixels
    :param marker: Marker symbol
    :param mouse_button: 1 = left click, 3 = right click
    :return: Pixel x and y coordinates as tuples inside a list
    """
    fig = list(map(plt.figure, plt.get_fignums()))[0]
    ax = fig.get_axes()[0]  # plt.gca()
    line, = ax.plot([], [], linestyle="none", marker=marker, color=color)
    picker = PixelPicker(line, ax, mouse_button)
    input("Press enter to stop picking pixels")
    return [class_num] + picker.get_pixels()


def generate_random_image(loc, title, h=200, w=200, old_ax=None):
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
    print(pixels)
