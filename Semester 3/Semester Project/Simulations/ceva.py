import os
import pickle as pkl
import matplotlib.pyplot as plt

baselines = ['zero', 'average', 'state', 'optimal_const', 'optimal_state']
dirs = [f'mdp_{b}_baseline' for b in baselines]

res = {}
for i in range(len(dirs)):
    file = os.listdir(f'results/{dirs[i]}')[0]
    file = f'results/{dirs[i]}/{file}/results.pkl'
    with open(file, 'rb') as f:
        data = pkl.load(f)
    res[baselines[i]] = data['returns'].mean(axis=1)

for b in baselines:
    plt.plot(res[b])
plt.legend(baselines)
plt.show()

