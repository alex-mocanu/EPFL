import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt

# Generate original image
img = np.zeros([16, 16])
img[4:12, 4:12] = 255

# Define filters
filters = [ np.array([[1, 1, 1], [0, 1, 1], [0, 0, 1]]),
            np.array([[1, 1, 1], [1, 1, 0], [1, 0, 0]]),
            np.array([[1, 0, 1], [0, 0, 0], [1, 0, 1]]),
            np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]),
            np.array([[1, 1, 1], [0, 0, 0], [0, 0, 0]]),
            np.array([[0, 0, 0], [0, 0, 0], [1, 0, 1]])]
# Normalize filters
filters = [fil / np.sum(fil) for fil in filters]

# Apply filters
filtered_imgs = []
for fil in filters:
    # Filter image
    fil_img = convolve2d(img, fil, 'same')
    # Normalize filtered image
    fil_img[fil_img>0] = 255
    filtered_imgs.append(fil_img)


# Plot filtered images
fig = plt.figure(1)
for i in range(2):
    for j in range(3):
        ind = 3 * i + j
        plt.subplot(int(f'23{ind+1}'))
        plt.imshow(filtered_imgs[ind], cmap='gray', vmin=0, vmax=255)
plt.show()
