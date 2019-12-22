import numpy as np
import matplotlib.pyplot as plt


def plot(cutoff, omega1, omega2, num_points, N):
    omegas = np.linspace(omega1, omega2, num_points).reshape(-1, 1)
    n = np.arange(-N, N + 1).reshape(1, -1)
    h = cutoff / np.pi * np.sinc(cutoff * n / np.pi)
    base = np.exp(-1j * np.dot(omegas, n))
    H = np.dot(base, h.T)
    fig, ax = plt.subplots(2, 1)
    ax[0].plot(omegas, np.abs(H))
    ax[0].set_xlabel('Frequency')
    ax[0].set_ylabel('Magnitude')
    ax[1].plot(omegas, np.angle(H))
    ax[1].set_xlabel('Frequency')
    ax[1].set_ylabel('Phase')
    plt.show()

    print('The peak is at', np.max(np.abs(H)))


if __name__ == '__main__':
    cutoff = np.pi / 2
    num_points = 2000
    N = 1000
    omega1, omega2 = 1.4, 1.7
    plot(cutoff, omega1, omega2, num_points, N)
