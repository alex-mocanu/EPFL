import gym
import numpy as np
from collections import defaultdict


class MDP(gym.Env):
    def __init__(self, rng, cfg):
        self.rng = rng
        self.init_env(cfg)
        self.ep_step = 0

    def init_env(self, cfg):
        '''
        Generate the structure of the environment
        :param argparser: argument parser used for providing the hyperparameters
        of the system
        '''
        self.num_states = cfg.num_states
        self.num_actions = cfg.num_actions
        self.num_features = cfg.num_features
        self.episode_length = cfg.episode_length
        self._sigma_r = cfg.sigma_r

        # Generate transition probabilities
        self._p = self.rng.dirichlet(np.ones(cfg.num_states),
                size=(cfg.num_states, cfg.num_actions))
        # Generate optimal policy parameters
        self._theta = self.rng.multivariate_normal(np.zeros(cfg.num_features),
                np.eye(cfg.num_features), size=(cfg.num_actions,))
        # Generate state features
        self._phi = self.rng.multivariate_normal(np.zeros(cfg.num_features),
            np.eye(cfg.num_features), size=(cfg.num_states,))
        # Generate the mean rewards
        self._mean_r = self._phi @ self._theta.T

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
        if self.ep_step > self.episode_length:
            done = True

        if not done:
            reward = self.generate_reward(self._state, action)
        else:
            reward = 0
        self._state = self.rng.choice(self.num_states, p=self._p[self._state, action])
        return self._state, reward, done, {}

    def reset(self):
        '''
        Reset the environment to a start state
        :return the start state
        '''
        self.ep_step = 0
        self._state = self.rng.choice(self.num_states)
        return self._state

    def set_state(self, state):
        '''
        Set the state of the environment
        :param state: state to be set
        '''
        self._state = state

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

    def export_env(self):
        '''
        Export environment setup
        :return dictionary containing environment setup
        '''
        return {
            'transition_probabilities': self._p,
            'env_parameters': self._theta,
            'state_features': self._phi
        }

    def import_env(self, settings):
        '''
        Import environment settings
        :param settings: environment settings
        '''
        self._p = settings['transition_probabilities']
        self._theta = settings['env_parameters']
        self._phi = settings['state_features']
        self._mean_r = self._phi @ self._theta.T


class MDP_v2(gym.Env):
    def __init__(self, rng, cfg):
        self.rng = rng
        self.init_env(cfg)
        self.ep_step = 0

    def init_env(self, cfg):
        '''
        Generate the structure of the environment
        :param cfg: configurations for the environment
        '''
        self.num_states = cfg.num_states
        self.num_actions = cfg.num_actions
        self.num_features = cfg.num_features
        self.episode_length = cfg.ep_size
        self._sigma_r = cfg.sigma_r

        # Generate transition probabilities
        self._p = self.rng.dirichlet(np.ones(cfg.num_states),
                size=(cfg.num_states, cfg.num_actions))
        # Generate optimal policy parameters
        self._theta = self.rng.multivariate_normal(np.zeros(cfg.num_features),
                np.eye(cfg.num_features))
        # Generate state, action features
        self._phi = self.rng.multivariate_normal(np.zeros(cfg.num_features),
            np.eye(cfg.num_features), size=(cfg.num_states,cfg.num_actions))
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
        if self.ep_step == self.episode_length:
            done = True

        if not done:
            reward = self.generate_reward(self._state, action)
        else:
            reward = 0
        self._state = self.rng.choice(self.num_states, p=self._p[self._state, action])

        return self._state, reward, done, {}

    def reset(self):
        '''
        Reset the environment to a start state
        :return the start state
        '''
        self.ep_step = 0
        self._state = self.rng.choice(self.num_states)
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
