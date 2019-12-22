import numpy as np
from gym.utils import seeding
from argparse import ArgumentParser
import matplotlib.pyplot as plt

from MDP import MDP, MDP_v2
from threeStateMDP import SimpleMDP
from continuous_cartpole import ContinuousCartPoleEnv
from agent import MDPAgent, MDPAgent_v2


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--task', type=str, default='mdp',
        help='the task to perform')
    argparser.add_argument('--num_episodes', type=int, default=100,
        help='the maximum number of episodes to run in a simulation')
    argparser.add_argument('--num_runs', type=int, default=100,
        help='number of trajectories to collect for an update')
    argparser.add_argument('--seed', type=int, default=1,
            help='random seed used for envvironment stochasticity')
    args = argparser.parse_args()

    # Initialize random number generator
    rng, _ = seeding.np_random(args.seed)

    # Initialize environment and agent
    if str.lower(args.task) == 'mdp':
        env = MDP(rng, argparser)
        agent = MDPAgent(env, rng, argparser)
    elif str.lower(args.task) == 'mdp_v2':
        env = MDP_v2(rng, argparser)
        agent = MDPAgent_v2(env, rng, argparser)
    elif str.lower(args.task) == 'smallmdp':
        env = SimpleMDP()
    elif str.lower(args.task) == 'pole':
        env = ContinuousCartPoleEnv()

    print('Env params:')
    print(env._theta)
    print('Initial agent params:')
    print(agent.theta)

    print('Start policy')
    print(agent._pi)

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
    # Run the simulation
    for ep in range(args.num_episodes):
        trajectories = []
        for _ in range(args.num_runs):
            trajectory = []
            obs = env.get_state()
            while True:
                action = agent.action(obs)
                new_obs, reward, done, _ = env.step(action)
                if done:
                    env.reset()
                    break
                trajectory.append((obs, action, reward))
                obs = new_obs
            trajectories.append(trajectory)
        # Optimize the agent
        agent.update(np.array(trajectories))

    print('Agent params:')
    print(agent.theta)
    print('Env mean reward:')
    print(env._mean_r)

    print('End policy')
    print(agent._pi)

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
