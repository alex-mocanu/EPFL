import unittest
import unittest.mock as mock
import numpy as np
from argparse import ArgumentParser
import MDP
from agent import MDPAgent


class TestMDPAgent(unittest.TestCase):
    @mock.patch('MDP.MDP')
    def setUp(self, mock_class):
        # Setup mock env
        mock_class.return_value.num_features = 2
        mock_class.return_value.action_space.n = 2
        self.env_features = np.array([[0, 1], [1, 0], [0.5, 0.5]])
        mock_class.return_value.get_features = mock.MagicMock(side_effect=lambda ind: self.env_features[ind].reshape(-1,1))
        mock_env = MDP.MDP()
        # Agent object
        self.agent = MDPAgent(mock_env, None, ArgumentParser())

    def test_policy_zero_theta(self):
        self.agent.theta = np.zeros((self.agent.env.action_space.n, self.agent.env.num_features))
        self.assertTrue(np.all(self.agent._policy(self.env_features[0].reshape(-1,1)) ==
            np.array([0.5, 0.5])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[1].reshape(-1,1)) ==
            np.array([0.5, 0.5])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[2].reshape(-1,1)) ==
            np.array([0.5, 0.5])))

    def test_policy_nonzero_theta(self):
        self.agent.theta = np.array([[1.,2.], [2.,1.]])
        self.assertTrue(np.all(self.agent._policy(self.env_features[0].reshape(-1,1)) ==
            np.array([np.exp(2) / np.exp([2,1]).sum(), np.exp(1) / np.exp([2,1]).sum()])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[1].reshape(-1,1)) ==
            np.array([np.exp(1) / np.exp([2,1]).sum(), np.exp(2) / np.exp([2,1]).sum()])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[2].reshape(-1,1)) ==
            np.array([0.5, 0.5])))

    def test_policy_grad_zero_theta(self):
        self.agent.theta = np.zeros((self.agent.env.action_space.n, self.agent.env.num_features))
        self.assertTrue(np.all(self.agent._policy(self.env_features[0].reshape(-1,1), 0) ==
            np.array([[0, 0.5], [0, -0.5]])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[0].reshape(-1,1), 1) ==
            np.array([[0, -0.5], [0, 0.5]])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[1].reshape(-1,1), 0) ==
            np.array([[0.5, 0], [-0.5, 0]])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[1].reshape(-1,1), 1) ==
            np.array([[-0.5, 0], [0.5, 0]])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[2].reshape(-1,1), 0) ==
            np.array([[0.25, 0.25], [-0.25, -0.25]])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[2].reshape(-1,1), 1) ==
            np.array([[-0.25, -0.25], [0.25, 0.25]])))

    def test_policy_grad_nonzero_theta(self):
        self.agent.theta = np.array([[1.,2.], [2.,1.]])
        policy = np.array([[np.exp(2) / np.exp([2,1]).sum(), np.exp(1) / np.exp([2,1]).sum()],
            [np.exp(1) / np.exp([1,2]).sum(), np.exp(2) / np.exp([1,2]).sum()],
            [0.5, 0.5]])
        self.assertTrue(np.all(self.agent._policy(self.env_features[0].reshape(-1,1), 0) ==
            np.array([(1 - policy[0,0]) * np.array([0,1]), -policy[0,1] * np.array([0,1])])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[0].reshape(-1,1), 1) ==
            np.array([-policy[0,0] * np.array([0,1]), (1 - policy[0,1]) * np.array([0,1])])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[1].reshape(-1,1), 0) ==
            np.array([(1 - policy[1,0]) * np.array([1,0]), -policy[1,1] * np.array([1,0])])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[1].reshape(-1,1), 1) ==
            np.array([-policy[1,0] * np.array([1,0]), (1 - policy[1,1]) * np.array([1,0])])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[2].reshape(-1,1), 0) ==
            np.array([(1 - policy[2,0]) * np.array([0.5,0.5]), -policy[2,1] * np.array([0.5,0.5])])))
        self.assertTrue(np.all(self.agent._policy(self.env_features[2].reshape(-1,1), 1) ==
            np.array([-policy[2,0] * np.array([0.5,0.5]), (1 - policy[2,1]) * np.array([0.5,0.5])])))

    def test_update_zero_theta(self):
        gamma, lr = 0.5, 0.1
        self.agent.gamma = gamma
        self.agent.lr = lr
        self.agent.theta = np.zeros((self.agent.env.action_space.n, self.agent.env.num_features))
        theta = self.agent.theta.copy()
        # Update the agent
        trajectories = np.array([[(0, 1, 0.5), (2, 0, 1), (1, 1, 0.75)]])
        self.agent.update(trajectories)
        # Compute the expected new theta
        policy = np.array([[0.5, 0.5], [0.5, 0.5], [0.5, 0.5]])
        returns = np.array([0.5 + gamma * 1 + gamma**2 * 0.75, gamma * 1 + gamma**2 * 0.75, gamma**2 * 0.75])
        grads = np.array([[-policy[0,0] * np.array([0,1]), (1 - policy[0,1]) * np.array([0,1])],
            [(1 - policy[2,0]) * np.array([0.5, 0.5]), -policy[2,1] * np.array([0.5, 0.5])],
            [-policy[1,0] * np.array([1,0]), (1 - policy[1,1]) * np.array([1,0])]])
        theta += lr * np.array([grads[0] * returns[0], grads[1] * returns[1], grads[2] * returns[2]]).mean(axis=0)
        self.assertTrue(np.all(self.agent.theta == theta))

    def test_update_nonzero_theta(self):
        gamma, lr = 0.5, 0.1
        self.agent.gamma = gamma
        self.agent.lr = lr
        self.agent.theta = np.array([[1.,2.], [2.,1.]])
        theta = self.agent.theta.copy()
        # Update the agent
        trajectories = np.array([[(0, 1, 0.5), (2, 0, 1), (1, 1, 0.75)]])
        self.agent.update(trajectories)
        # Compute the expected new theta
        policy = np.array([[np.exp(2) / np.exp([2,1]).sum(), np.exp(1) / np.exp([2,1]).sum()],
            [np.exp(1) / np.exp([1,2]).sum(), np.exp(2) / np.exp([1,2]).sum()],
            [0.5, 0.5]])
        returns = np.array([0.5 + gamma * 1 + gamma**2 * 0.75, gamma * 1 + gamma**2 * 0.75, gamma**2 * 0.75])
        grads = np.array([[-policy[0,0] * np.array([0,1]), (1 - policy[0,1]) * np.array([0,1])],
            [(1 - policy[2,0]) * np.array([0.5, 0.5]), -policy[2,1] * np.array([0.5, 0.5])],
            [-policy[1,0] * np.array([1,0]), (1 - policy[1,1]) * np.array([1,0])]])
        theta += lr * np.array([grads[0] * returns[0], grads[1] * returns[1], grads[2] * returns[2]]).mean(axis=0)
        self.assertTrue(np.all(self.agent.theta == theta))


if __name__ == '__main__':
    unittest.main()
