import gym
from gym import spaces
from gym.utils import seeding
import numpy as np


class SimpleMDP(gym.Env):
    def __init__(self):
        self.state_space = spaces.Discrete(3)
        self.action_space = spaces.Discrete(2)
        self.transition = np.array([
            [[0.0, 0.8, 0.2],
            [0.8, 0.0, 0.2],
            [0.0, 0.8, 0.2]],
            [[0.0, 0.2, 0.8],
            [0.2, 0.0, 0.8],
            [0.0, 0.2, 0.8]]])
        self.rewards = np.array([0, 0, 1])
        self.features = np.array([[2/3, 1/3], [1/3, 2/3], [5/18, 5/18]])
        self.max_iter = 100

        self.seed()
        self.state = 0
        self.iter = 0

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        self.iter += 1
        self.state = self.np_random.choice(range(self.state_space.n), p=self.transition[action][self.state])
        done = (self.iter == self.max_iter)

        if not done:
            reward = self.rewards[self.state]
        else:
            reward = 0

        return self.state, reward, done, {}

    def reset(self):
        self.iter = 0
        self.state = self.state_space.sample()
        return self.state
