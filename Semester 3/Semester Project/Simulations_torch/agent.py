import torch
import numpy as np


class MDPAgent:
    def __init__(self, env, rng, argparser):
        torch.manual_seed(2)
        self.env = env
        self.rng = rng
        # self.theta = self.rng.normal(0, 1, (self.env.action_space.n, self.env.num_features))
        self.theta = torch.nn.Linear(self.env.num_features, self.env.action_space.n)

        argparser.add_argument('--lr', type=float, default=0.001,
            help='learning rate')
        argparser.add_argument('--gamma', type=float, default=0.99,
            help='discount factor for computing the return')
        args = argparser.parse_args()
        self.lr = args.lr
        self.gamma = args.gamma

        self.optimizer = torch.optim.SGD(self.theta.parameters(), args.lr, momentum=0)

    def action(self, obs):
        '''
        Agent's action under a given observation
        :param obs: observation received from the environment
        :return agent's action
        '''
        features = self.env.get_features(obs)
        probs = self._policy(features)
        return self.rng.choice(range(self.env.action_space.n), p=probs.detach().numpy())

    def update(self, trajectory, baseline=0):
        '''
        Update the agent's parameter with the policy gradient
        :param trajectory: list of (state, action, reward) tuples in the episode
        :param baseline: baseline used in the update
        :return total discounted reward collected in the episode
        '''
        ep_len = trajectory.shape[0]
        rewards = np.array([reward for _, _, reward in trajectory])
        discount_factors = np.array([self.gamma**step for step in range(ep_len)])
        returns = np.flip(np.flip(discount_factors * rewards).cumsum())
        # log_grads = np.array([self._policy(self.env.get_features(np.int(state)), np.int(action))
        #     for state, action, _ in trajectory])
        # grad_return = log_grads.reshape(ep_len,-1) * (returns - baseline).reshape(-1,1)

        # Update parameters
        # self.theta += self.lr * grad_return.sum(axis=0).reshape(self.theta.shape) / ep_len
        log_probs = np.array([torch.log(self._policy(self.env.get_features(np.int(state)))[np.int(action)])
            for state, action, _ in trajectory])

        self.optimizer.zero_grad()
        out = ((log_probs * (returns - baseline)).sum() / ep_len).backward()
        self.optimizer.step()

        return returns[0]

    def _policy(self, features, log_grad=-1):
        '''
        Compute the policy or the log gradient of the policy for a given action
        :param features: the features for the state
        :param log_grad: index of action for which to compute the log gradient
        :return the policy or the log grad of the policy
        '''
        # coefs = self.theta @ features
        # probs = np.exp(coefs) / np.exp(coefs).sum()
        # if log_grad == -1:
        #     return probs.flatten()
        # else:
        #     res = -probs @ features.T
        #     res[log_grad, :] += features.flatten()
        #     return res
        coefs = self.theta(torch.Tensor(features))
        return torch.nn.functional.softmax(coefs, dim=0)
