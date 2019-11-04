import matplotlib.pyplot as plt
import numpy as np


def generate_random_image(loc, title, h=28, w=28, old_ax=None):
    img = (np.random.standard_normal([h, w, 3]) * 255).astype(np.uint8)
    ax = plt.subplot(loc) if old_ax is None else plt.subplot(loc, sharex=old_ax, sharey=old_ax)
    # ax.set_adjustable('box')
    plt.title(title)
    plt.axis('off')
    plt.imshow(img)
    return ax


def generate_test_figure():
    plt.figure(1, figsize=(8, 10))
    plt.clf()
    plt.ion()
    ax = generate_random_image(211, "test1", h=28, w=28)
    generate_random_image(212, "test2", h=28, w=28, old_ax=ax)
    plt.tight_layout()
    plt.show()
    input("Press enter to close")


if __name__ == '__main__':
    generate_test_figure()
