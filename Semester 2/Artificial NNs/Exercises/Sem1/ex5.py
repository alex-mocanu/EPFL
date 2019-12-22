import numpy as np
import matplotlib.pyplot as plt


alpha = 2
x = np.array([[1,1], [1,-1], [alpha,2], [alpha,1], [alpha,-2], [alpha,-1],
    [-1,3], [-1,2], [-1,1], [-1,-1], [-1,-2], [-1,-3]])
t = np.array([1]*6 + [0]*6)

# Plot positive and negative samples
x_pos, y_pos = [e[0] for e in x[:6]], [e[1] for e in x[:6]]
x_neg, y_neg = [e[0] for e in x[6:]], [e[1] for e in x[6:]]
plt.scatter(x_pos, y_pos, marker='+')
plt.scatter(x_neg, y_neg, marker='o')
plt.show()
