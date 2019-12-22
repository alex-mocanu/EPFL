from __future__ import division
import numpy as np
import matplotlib.pylab as plt
import scipy as sp
import scipy.signal


def compute_y(N):
    h = np.array([0, 0.5, 0.25, 0.25])
    # generate x[n]
    x = np.sqrt(3) * np.random.randn(N)
    # filter it with h[n]
    x1 = np.concatenate((x[-3:], x, x[:3]))
    y1 = sp.signal.lfilter(h, 1., x1)[3:N + 3]
    # generate z[n]
    z = np.random.randn(N)
    # generate y[n]
    y = y1 + z
    return y


def estimate_psd(N, M):
    """
    :param N: the length of the input vector
    :param M: the number of iterations
    :return:
    """
    PSD = np.zeros(N, dtype=float)
    for loop in range(M):
        PSD += np.abs(np.fft.fft(compute_y(N))) ** 2 / N
    return PSD / M


if __name__ == '__main__':
    N = 100
    # compare the experimental PSD to the theoretical PSD
    # for varying values of M
    for count, M in enumerate([50, 500, 5000]):
        PSD = estimate_psd(N, M)
        omega = np.linspace(0, 2 * np.pi, num=N)
        PSD_theo = 17 / 8. + 9 / 8. * np.cos(omega) + 3 / 4. * np.cos(2 * omega)
        plt.figure(num=count, figsize=(5, 3), dpi=90)
        plt.plot(PSD, 'r--', label='estimate')
        plt.plot(PSD_theo, 'b-', label='theoretical')
        plt.legend()
        plt.show()
