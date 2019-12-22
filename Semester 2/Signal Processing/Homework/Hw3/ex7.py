import numpy as np
import matplotlib.pyplot as plt


def mod(M, omega):
    up = (np.cos(omega * M) - 1)**2 + np.sin(omega * M)**2
    down = (np.cos(omega) - 1)**2 + np.sin(omega)**2
    return np.sqrt(up / down)

def run_fft(N):
    x = np.array([1] * min(M, N) + [0] * (N - min(M, N)))
    fft = np.fft.fft(x, n=N)
    x = np.linspace(-np.pi, np.pi, N)
    y = list(map(lambda x: np.absolute(x), fft))
    return x, y[int(N/2):] + y[:int(N/2)]

if __name__ == '__main__':
    M = 20

    Ns = [30, 50, 100, 1000]
    f, ax = plt.subplots(1, len(Ns) + 1)

    # Analytical
    num_samples = 10000
    x = np.linspace(-np.pi, np.pi, num_samples)
    y = list(map(lambda x: mod(M, x), x))
    ax[0].set_title('Analytical')
    ax[0].plot(x, y)

    # FFT
    for i, N in enumerate(Ns):
        x, y = run_fft(N)
        ax[i + 1].set_title(f'FFT {N}')
        ax[i + 1].plot(x, y)
    plt.show()
