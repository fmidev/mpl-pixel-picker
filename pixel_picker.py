import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

# When plotting in matplotlib the upper left corner has the values of:
Y_OFFSET = - 0.5
X_OFFSET = -0.5


class PixelPicker:
    def __init__(self, figure, rect_colls, mouse_button):
        self.xys = set()
        self.rects = []
        self.figure = figure
        self.axs = figure.get_axes()
        self.rect_colls = rect_colls
        self.mouse_button = mouse_button
        self.cid = figure.canvas.mpl_connect('button_press_event', self._on_click)
        self.cidmotion = figure.canvas.mpl_connect('motion_notify_event', self._on_motion)

    def _on_click(self, event):
        # print('click', event)
        if self._valid_event(event):
            self._add_rectangle(event)

    def _on_motion(self, event):
        # print('motion', event)
        if self._valid_event(event):
            self._add_rectangle(event)

    def _valid_event(self, event):
        return event.inaxes in self.axs and event.button == self.mouse_button

    def _add_rectangle(self, event):
        xy = (int(round(event.xdata)), int(round(event.ydata)))
        size_before = len(self.xys)
        self.xys.add(xy)
        if len(self.xys) > size_before:
            self.rects.append(Rectangle((xy[0] + X_OFFSET, xy[1] + Y_OFFSET), 1, 1))
            for rect_coll in self.rect_colls:
                rect_coll.set_paths(self.rects)
            self.figure.canvas.draw()

    def get_pixels(self):
        return [xy for xy in self.xys]

    def clear(self):
        for rect_coll in self.rect_colls:
            rect_coll.set_paths([])
        self.figure.canvas.draw()


def pick_pixels(class_num=0, color=(1, 0, 0, 0.7), mouse_button=3):
    """

    :param class_num: Number of the class
    :param color: Color of the painted pixels
    :param mouse_button: 1 = left click, 3 = right click
    :return: Class number and after that pixel x and y coordinates as tuples inside a list
    """
    fig = list(map(plt.figure, plt.get_fignums()))[0]
    rect_colls = []
    for axes in fig.get_axes():
        rectangle_collection = PatchCollection([], facecolors=color, edgecolors=color)
        axes.add_collection(rectangle_collection)
        rect_colls.append(rectangle_collection)

    picker = PixelPicker(fig, rect_colls, mouse_button)
    input("Press enter to stop picking pixels")
    pixels = [class_num] + picker.get_pixels()
    picker.clear()
    return pixels


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
