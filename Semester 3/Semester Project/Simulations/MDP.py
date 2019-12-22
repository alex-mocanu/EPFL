import gym
from gym import spaces
import numpy as np
from argparse import ArgumentParser
from collections import defaultdict


class MDP(gym.Env):
    def __init__(self, rng, argparser):
        self.rng = rng
        self.init_env(argparser)
        self.ep_step = 0

    def init_env(self, argparser):
        '''
        Generate the structure of the environment
        :param argparser: argument parser used for providing the hyperparameters
        of the system
        '''
        argparser.add_argument('--num_states', type=int, default=10,
            help='number of states')
        argparser.add_argument('--num_actions', type=int, default=3,
            help='number of actions')
        argparser.add_argument('--num_features', type=int, default=2,
            help='number of features to represent a state')
        argparser.add_argument('--ep_size', type=int, default=100,
            help='number of steps in an episode')
        argparser.add_argument('--sigma_r', type=int, default=0.1,
            help='standard deviation of the reward generator')
        args = argparser.parse_args()

        self.state_space = spaces.Discrete(args.num_states)
        self.action_space = spaces.Discrete(args.num_actions)
        self.num_features = args.num_features
        self.episode_size = args.ep_size
        self._sigma_r = args.sigma_r

        # Generate transition probabilities
        self._p = self.rng.dirichlet(np.ones(args.num_states),
                size=(args.num_states, args.num_actions))
        # Generate optimal policy parameters
        self._theta = self.rng.multivariate_normal(np.zeros(args.num_features),
                np.eye(args.num_features), size=(args.num_actions,))
        # Generate state features
        self._phi = self.rng.multivariate_normal(np.zeros(args.num_features),
            np.eye(args.num_features), size=(args.num_states,))
        # Generate the mean rewards
        self._mean_r = self._phi @ self._theta.T

        print('Features:')
        print(self._phi)

    def generate_reward(self, state, action):
        '''
        Generate a stochastic reward for a given state and action
        :param state: current state
        :param action: current action
        :return random reward for the state and action
        '''
        return self.rng.normal(self._mean_r[state, action], self._sigma_r)

    def step(self, action):
        '''
        Apply an action and observe the transition
        :param action: the action to apply on the environment
        :return the new state, the reward and whether the state is terminal
        '''
        self.ep_step += 1
        done = False
        if self.ep_step == self.episode_size:
            done = True

        if not done:
            reward = self.generate_reward(self._state, action)
        else:
            reward = 0
        self._state = self.rng.choice(range(self.state_space.n),
                p=self._p[self._state, action])

        return self._state, reward, done, {}

    def reset(self):
        '''
        Reset the environment to a start state
        :return the start state
        '''
        self.ep_step = 0
        self._state = self.state_space.sample()
        return self._state

    def get_state(self):
        '''
        Return the current state of the enviroment
        :return the current state
        '''
        return self._state

    def get_features(self, state=-1):
        '''
        Return the features corresponding to a state in form of a column vector
        :param state: the state for which we want to get the features, -1 if we
        want to retrieve all the features
        :return the features for the state
        '''
        if state == -1:
            return self._phi
        return self._phi[state].reshape(-1, 1)


class MDP_v2(gym.Env):
    def __init__(self, rng, argparser):
        self.rng = rng
        self.init_env(argparser)
        self.ep_step = 0

    def init_env(self, argparser):
        '''
        Generate the structure of the environment
        :param argparser: argument parser used for providing the hyperparameters
        of the system
        '''
        argparser.add_argument('--num_states', type=int, default=10,
            help='number of states')
        argparser.add_argument('--num_actions', type=int, default=2,
            help='number of actions')
        argparser.add_argument('--num_features', type=int, default=2,
            help='number of features to represent a state')
        argparser.add_argument('--ep_size', type=int, default=100,
            help='number of steps in an episode')
        argparser.add_argument('--sigma_r', type=int, default=0,
            help='standard deviation of the reward generator')
        args = argparser.parse_args()

        self.state_space = spaces.Discrete(args.num_states)
        self.action_space = spaces.Discrete(args.num_actions)
        self.num_features = args.num_features
        self.episode_size = args.ep_size
        self._sigma_r = args.sigma_r

        # Generate transition probabilities
        self._p = self.rng.dirichlet(np.ones(args.num_states),
                size=(args.num_states, args.num_actions))
        # Generate optimal policy parameters
        self._theta = self.rng.multivariate_normal(np.zeros(args.num_features),
                np.eye(args.num_features))
        # Generate state, action features
        self._phi = self.rng.multivariate_normal(np.zeros(args.num_features),
            np.eye(args.num_features), size=(args.num_states,args.num_actions))
        # Generate the mean rewards
        self._mean_r = self._phi @ self._theta

    def generate_reward(self, state, action):
        '''
        Generate a stochastic reward for a given state and action
        :param state: current state
        :param action: current action
        :return random reward for the state and action
        '''
        return self.rng.normal(self._mean_r[state, action], self._sigma_r)

    def step(self, action):
        '''
        Apply an action and observe the transition
        :param action: the action to apply on the environment
        :return the new state, the reward and whether the state is terminal
        '''
        self.ep_step += 1
        done = False
        if self.ep_step == self.episode_size:
            done = True

        if not done:
            reward = self.generate_reward(self._state, action)
        else:
            reward = 0
        self._state = self.rng.choice(range(self.state_space.n),
                p=self._p[self._state, action])

        return self._state, reward, done, {}

    def reset(self):
        '''
        Reset the environment to a start state
        :return the start state
        '''
        self.ep_step = 0
        self._state = self.state_space.sample()
        return self._state

    def get_state(self):
        '''
        Return the current state of the enviroment
        :return the current state
        '''
        return self._state

    def get_features(self, state):
        '''
        Return the features corresponding to a state
        :param state: the state for which we want to get the features
        :return the features for the state
        '''
        return self._phi[state]
