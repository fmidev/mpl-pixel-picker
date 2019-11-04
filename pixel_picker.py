import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

# When plotting in matplotlib the upper left corner has the values of:
Y_OFFSET = - 0.5
X_OFFSET = -0.5


class PixelPicker:
    def __init__(self, figure, rect_coll, mouse_button):
        self.rects = set()
        self.figure = figure
        self.rect_coll = rect_coll
        self.mouse_button = mouse_button
        self.cid = figure.canvas.mpl_connect('button_press_event', self)
        self.cidmotion = figure.canvas.mpl_connect('motion_notify_event', self._on_motion)

    def __call__(self, event):
        # print('click', event)
        if event.inaxes != self.figure.get_axes()[0] or event.button != self.mouse_button: return
        self._add_rectangle(event)

    def _on_motion(self, event):
        # print('motion', event)
        if event.inaxes != self.figure.get_axes()[0] or event.button != self.mouse_button: return
        self._add_rectangle(event)

    def _add_rectangle(self, event):
        xy = (int(round(event.xdata)) + X_OFFSET, int(round(event.ydata)) + Y_OFFSET)
        size_before = len(self.rects)
        self.rects.add(Rectangle(xy, 1, 1))
        if len(self.rects) > size_before:
            self.rect_coll.set_paths(self.rects)
            self.figure.canvas.draw()

    def get_pixels(self):
        return [(x - X_OFFSET, y - Y_OFFSET) for x, y in map(lambda r: r.xy, self.rects)]


def pick_pixels(class_num=0, color=(1, 0, 0, 0.7), mouse_button=3):
    """

    :param class_num: Number of the class
    :param color: Color of the painted pixels
    :param mouse_button: 1 = left click, 3 = right click
    :return: Class number and after that pixel x and y coordinates as tuples inside a list
    """
    fig = list(map(plt.figure, plt.get_fignums()))[0]
    ax = fig.get_axes()[0]  # plt.gca()
    rect_coll = PatchCollection([], facecolors=color, edgecolors=color)
    ax.add_collection(rect_coll)
    picker = PixelPicker(fig, rect_coll, mouse_button)
    input("Press enter to stop picking pixels")
    return [class_num] + picker.get_pixels()


def generate_random_image(loc, title, h=60, w=60, old_ax=None):
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
