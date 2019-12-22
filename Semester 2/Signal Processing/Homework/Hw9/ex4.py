import IPython
import numpy as np
import matplotlib.pyplot as plt


def chirp(a, b, sf, len=1):
    t = np.arange(0, len, 1 / sf)
    return np.cos(np.pi * a * t**2 + 2 * np.pi * b * t), t


if __name__ == '__main__':
    # Generate samples
    samples_40, time_40 = chirp(40, 4, 400)
    samples_400, time_400 = chirp(400, 4, 400)
    # Plot samples
    fig, ax = plt.subplots(1, 2, figsize=(20, 4))
    ax[0].plot(time_40, samples_40)
    ax[1].plot(time_400, samples_400)
    plt.show()
