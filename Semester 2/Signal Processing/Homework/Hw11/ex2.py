import sys
import numpy as np
import matplotlib.pyplot as plt


if len(sys.argv) < 2:
    print('Usage: python ex2.py IMG_SIZE')
else:
    N = int(sys.argv[1])

# Set initial conditions
a = np.zeros([N, N])
a[0,N-1] = a[N-1,0] = 255

# Generate the whole image
for i in range(N):
    for j in range(N):
        a[i,j] = (  (N - i - 1) * (N - j - 1) * a[0,0] +
                    (N - i - 1) * j * a[0,N-1] +
                    i * (N - j - 1) * a[N-1,0] +
                    i * j * a[N-1,N-1]) / (N - 1)**2

# Show the image
plt.imshow(a, cmap='gray', vmin=0, vmax=255)
plt.show()
