import numpy as np


class MDPAgent:
    def __init__(self, env, rng, argparser):
        self.env = env
        self.rng = rng
        self.theta = np.zeros((self.env.action_space.n, self.env.num_features))

        argparser.add_argument('--lr', type=float, default=1,
            help='learning rate')
        argparser.add_argument('--gamma', type=float, default=0.95,
            help='discount factor for computing the return')
        args = argparser.parse_args()
        self.lr = args.lr
        self.gamma = args.gamma

        self._pi = np.ones((self.env.state_space.n, self.env.action_space.n)) / self.env.action_space.n

    def action(self, obs):
        '''
        Agent's action under a given observation
        :param obs: observation received from the environment
        :return agent's action
        '''
        return self.rng.choice(range(self.env.action_space.n), p=self._pi[obs])

    def update(self, trajectories, baseline=0):
        '''
        Update the agent's parameter with the policy gradient
        :param trajectory: list of (state, action, reward) tuples in the episode
        :param baseline: baseline used in the update
        :return total discounted reward collected in the episode
        '''
        ep_len = trajectories.shape[1]
        average_grad_return = np.zeros((ep_len, self.theta.shape[0] * self.theta.shape[1]))
        for trajectory in trajectories:
            rewards = np.array([reward for _, _, reward in trajectory])
            discount_factors = np.array([self.gamma**step for step in range(ep_len)])
            returns = np.flip(np.flip(discount_factors * rewards).cumsum())
            log_grads = np.array([self._policy_log_grad(np.int(state), np.int(action))
                for state, action, _ in trajectory])
            grad_return = log_grads.reshape(ep_len,-1) * (returns - baseline).reshape(-1,1)
            average_grad_return += grad_return
        average_grad_return /= trajectories.shape[0]

        # Update parameters
        self.theta += self.lr * average_grad_return.mean(axis=0).reshape(self.theta.shape)
        # Update the policy
        coefs = self.env.get_features() @ self.theta.T
        self._pi = np.exp(coefs) / np.exp(coefs).sum(axis=1).reshape(-1, 1)

    def _policy_log_grad(self, state, action):
        '''
        Compute the policy or the log gradient of the policy for a given action
        :param state: index of state for which to compute the log gradient
        :param action: index of action for which to compute the log gradient
        :return the policy or the log grad of the policy
        '''
        features = self.env.get_features(state)
        res = -self._pi[state].reshape(-1,1) @ features.T
        res[action] += features.flatten()
        return res


class MDPAgent_v2:
    def __init__(self, env, rng, argparser):
        self.env = env
        self.rng = rng
        self.theta = np.zeros(self.env.num_features)

        argparser.add_argument('--lr', type=float, default=10,
            help='learning rate')
        argparser.add_argument('--gamma', type=float, default=0,
            help='discount factor for computing the return')
        args = argparser.parse_args()
        self.lr = args.lr
        self.gamma = args.gamma

    def action(self, obs):
        '''
        Agent's action under a given observation
        :param obs: observation received from the environment
        :return agent's action
        '''
        features = self.env.get_features(obs)
        probs = self._policy(features)
        return self.rng.choice(range(self.env.action_space.n), p=probs)

    def update(self, trajectories, baseline=0):
        '''
        Update the agent's parameter with the policy gradient
        :param trajectory: list of (state, action, reward) tuples in the episode
        :param baseline: baseline used in the update
        :return total discounted reward collected in the episode
        '''
        ep_len = trajectories.shape[1]
        average_grad_return = np.zeros((ep_len, self.theta.size))
        for trajectory in trajectories:
            rewards = np.array([reward for _, _, reward in trajectory])
            discount_factors = np.array([self.gamma**step for step in range(ep_len)])
            returns = np.flip(np.flip(discount_factors * rewards).cumsum())
            log_grads = np.array([self._policy(self.env.get_features(np.int(state)), np.int(action))
                for state, action, _ in trajectory])
            grad_return = log_grads * (returns - baseline).reshape(-1,1)
            average_grad_return += grad_return
        average_grad_return /= trajectories.shape[0]

        # Update parameters
        self.theta += self.lr * average_grad_return.mean(axis=0)

    def _policy(self, features, action=-1):
        '''
        Compute the policy or the log gradient of the policy for a given action
        :param features: the features for the state
        :param action: index of action for which to compute the log gradient
        :return the policy or the log grad of the policy
        '''
        coefs = features @ self.theta
        probs = np.exp(coefs) / np.exp(coefs).sum()
        if action == -1:
            return probs
        else:
            return features[action] - (features * probs.reshape(-1,1)).sum(axis=0)
