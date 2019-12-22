import numpy as np
from gym.utils import seeding
from argparse import ArgumentParser
import matplotlib.pyplot as plt

from MDP import MDP
from threeStateMDP import SimpleMDP
from continuous_cartpole import ContinuousCartPoleEnv
from agent import MDPAgent


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--task', type=str, default='mdp',
        help='the task to perform')
    argparser.add_argument('--num_episodes', type=int, default=1000,
        help='the maximum number of episodes to run in a simulation')
    argparser.add_argument('--seed', type=float, default=1,
            help='random seed used for envvironment stochasticity')
    args = argparser.parse_args()

    # Initialize random number generator
    rng, _ = seeding.np_random(args.seed)

    # Initialize environment and agent
    if str.lower(args.task) == 'mdp':
        env = MDP(rng, argparser)
        agent = MDPAgent(env, rng, argparser)
    elif str.lower(args.task) == 'smallmdp':
        env = SimpleMDP()
    elif str.lower(args.task) == 'pole':
        env = ContinuousCartPoleEnv()

    print('Env params:')
    print(env._theta)
    print('Initial agent params:')
    print(agent.theta)

    print('Start policy')
    for state in range(env.state_space.n):
        print(agent._policy(env.get_features(state)))

    print('Start expected return')
    ret = 0
    for _ in range(100):
        env.reset()
        obs = env.get_state()
        step = 0
        while True:
            action = agent.action(obs)
            obs, reward, done, _ = env.step(action)
            ret += agent.gamma**step * reward
            step += 1
            if done:
                env.reset()
                break
    print(ret / 100)

    env.reset()
    returns = []
    # Run the simulation
    for ep in range(args.num_episodes):
        trajectory = []
        obs = env.get_state()
        while True:
            action = agent.action(obs)
            obs, reward, done, _ = env.step(action)
            trajectory.append((obs, action, reward))
            if done:
                env.reset()
                break
        # Optimize the agent
        ret = agent.update(np.array(trajectory))
        if ep % 10 == 0:
            returns.append(ret)
        # print(f'Return: {agent.update(np.array(trajectory))}')
    plt.plot(returns)
    plt.show()

    print('Agent params:')
    print(agent.theta)
    print('Env mean reward:')
    print(env._mean_r)

    print('End policy')
    for state in range(env.state_space.n):
        print(agent._policy(env.get_features(state)))

    print('End expected return')
    ret = 0
    for _ in range(100):
        env.reset()
        obs = env.get_state()
        step = 0
        while True:
            action = agent.action(obs)
            obs, reward, done, _ = env.step(action)
            ret += agent.gamma**step * reward
            step += 1
            if done:
                env.reset()
                break
    print(ret / 100)

    env.close()
