import numpy as np

def sigm(x, b):
    return np.e**(-b*x)/(1+np.e**(-b*x))**2

def train(w, x, t, g, b):
    for i in range(len(x)):
        pred = 0.5 * (1 + np.sign(w.dot(x[i])))
        diff = t[i] - pred
        d = sigm(w.dot(x[i]),b)
        w += g * diff * d * x[i]
        print(w)

x = np.array([[2,-1], [-1,1], [2,0.5], [0.2,-0.2], [0.5,-1], [2,1]])
t = np.array([1,0,1,0,1,0], dtype=np.float64)
w = np.array([1,0], dtype=np.float64)
train(w, x, t, 2, 0.5)
