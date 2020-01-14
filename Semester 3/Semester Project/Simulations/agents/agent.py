import numpy as np
from .baselines import get_baseline


class MDPAgent:
    def __init__(self, env, rng, cfg):
        self.env = env
        self.rng = rng
        self.theta = np.zeros((self.env.num_actions, self.env.num_features))
        self.lr = cfg.lr
        self.gamma = cfg.gamma
        # Agent policy
        self._pi = np.ones((self.env.num_states, self.env.num_actions)) / self.env.num_actions
        # Baseline
        self.baseline = get_baseline(env, self, cfg.baseline)
        self.exact_baseline = cfg.baseline.exact

    def action(self, obs):
        '''
        Agent's action under a given observation
        :param obs: observation received from the environment
        :return agent's action
        '''
        return self.rng.choice(self.env.num_actions, p=self._pi[obs])

    def update(self, trajectories):
        '''
        Update the agent's parameter with the policy gradient
        :param trajectory: list of (state, action, reward) tuples in the episode
        :return total discounted reward collected in the episode
        '''
        # Compute the baseline for the current policy
        self.baseline.compute(self.exact_baseline)
        # Aggregate results from the trajectories
        ep_len = trajectories.shape[1]
        returns, grads = [], []
        for trajectory in trajectories:
            rewards = np.array([reward for _,_,reward in trajectory])
            discount_factors = np.array([self.gamma**step for step in range(ep_len)])
            ret = np.flip(np.flip(discount_factors * rewards).cumsum())
            log_grads = np.array([self._policy_log_grad(np.int(state), np.int(action))
                for state, action, _ in trajectory]).reshape(ep_len, -1)

            baseline_val = self.baseline.get_baseline(trajectory)
            if len(baseline_val.shape) < 2:
                baseline_ret = (ret - baseline_val).reshape(-1,1)
            else:
                baseline_ret = (ret - baseline_val.T).T
            grad_return = log_grads * baseline_ret

            # Cumulate reward and gradient estimation
            returns.append(ret[0])
            grads.append(grad_return)
        grads = np.array(grads)

        # Update parameters
        self.theta += self.lr * grads.mean(axis=(0,1)).reshape(self.theta.shape)
        # Update the policy
        coefs = self.env.get_features() @ self.theta.T
        self._pi = np.exp(coefs) / np.exp(coefs).sum(axis=1).reshape(-1, 1)

        return returns, grads

    def set_parameters(self, theta):
        '''
        Set the agent parameters
        :param theta: agent parameters to set
        '''
        self.theta = theta
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
    def __init__(self, env, rng, cfg):
        self.env = env
        self.rng = rng
        self.theta = np.zeros(self.env.num_features)

        self.lr = cfg.lr
        self.gamma = cfg.gamma

    def action(self, obs):
        '''
        Agent's action under a given observation
        :param obs: observation received from the environment
        :return agent's action
        '''
        features = self.env.get_features(obs)
        probs = self._policy(features)
        return self.rng.choice(self.env.num_actions, p=probs)

    def update(self, trajectories, baseline=0):
        '''
        Update the agent's parameter with the policy gradient
        :param trajectory: list of (state, action, reward) tuples in the episode
        :param baseline: baseline used in the update
        :return total discounted reward collected in the episode
        '''
        ep_len = trajectories.shape[1]
        average_return = 0
        average_grad_return = np.zeros((ep_len, self.theta.size))
        for trajectory in trajectories:
            rewards = np.array([reward for _, _, reward in trajectory])
            discount_factors = np.array([self.gamma**step for step in range(ep_len)])
            returns = np.flip(np.flip(discount_factors * rewards).cumsum())
            log_grads = np.array([self._policy(self.env.get_features(np.int(state)), np.int(action))
                for state, action, _ in trajectory])
            grad_return = log_grads * (returns - baseline).reshape(-1,1)
            # Cumulate return and gradient estimation
            average_return += returns[0]
            average_grad_return += grad_return
        # Normalize return and gradient estimation
        average_return /= trajectories.shape[0]
        average_grad_return /= trajectories.shape[0]

        # Update parameters
        self.theta += self.lr * average_grad_return.mean(axis=0)

        return average_return

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
