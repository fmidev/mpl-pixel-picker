# mpl-pixel-picker

*Joona Laine, Sanna Hautala, Spatineo Oy*

A tool to pick pixel coordinates from Matplotlib plotted images

## Getting Started

### Prerequisites

Tested versions

* Python 3.6.9
* matplotlib==3.1.1
* numpy==1.17.3
* tkinter==8.6.9 (optional)

### Basic use of the tool

#### Example 1: Basic use with one image

```Python
import matplotlib.pyplot as plt
import numpy as np
from pixel_picker import pick_pixels
# Draw random image
plt.figure(1, figsize=(8, 10))
plt.ion()
plt.imshow((np.random.standard_normal([100, 100, 3]) * 255).astype(np.uint8))
plt.show()
# Pick pixels
pick_pixels()
```

#### Example 2: Basic use with two images

```Python
import matplotlib.pyplot as plt
import numpy as np
from pixel_picker import pick_pixels
# Draw two random images
plt.figure(1, figsize=(8, 10))
plt.ion()
ax = plt.subplot(211)
plt.imshow((np.random.standard_normal([100, 100, 3]) * 255).astype(np.uint8))
ax2 = plt.subplot(212, sharex=ax, sharey=ax)
plt.imshow((np.random.standard_normal([100, 100, 3]) * 255).astype(np.uint8))
plt.show()
# Pick pixels
pick_pixels()
```

### Return

Class number and after that pixel x and y coordinates as tuples inside a list:

`[0, (41, 13), (37, 10), (42, 10), (40, 22), (46, 25)]`

### Parameters of pick_pixels

**class_num:** Number of the class

**radius:** Radius of the drawing circle (0 = 1 pixel)

**color:** Color of the painted pixels (supports opacity): `(1, 0, 0, 0.5)`

**pick_button:** 1 = left click, 2 = middle click, 3 = right click, None = no button

**erase_button:** 1 = left click, 2 = middle click, 3 = right click, None = no button

**reset_button:** 1 = left click, 2 = middle click, 3 = right click, None = no button

**is_interpolation_used:** True = Interpolates points in between when moving mouse too fast, False = No interpolation

**picked_coordinates:** Already picked coordinates. Format: Class number and after that pixel x and y coordinates as tuples inside a list or tuple: `[0, (41, 13), (37, 10), (42, 10), (40, 22), (46, 25)]`

**use_gui:** True = Use graphical ui if tkinter is installed, False = use command line option

#### Example code for using parameters

```pick_pixels(class_num=3, radius=0)```
