import os
import sys
import yaml
import numpy as np
from gym.utils import seeding
from argparse import ArgumentParser, Namespace
import pickle as pkl
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from envs.MDP import MDP, MDP_v2
from envs.threeStateMDP import SimpleMDP
from envs.continuous_cartpole import ContinuousCartPoleEnv
from agents.agent import MDPAgent, MDPAgent_v2


def dict_to_namespace(dct):
    '''
    Transform dictionary to namespace
    :param dct: dictionary to transform
    :return namespace corresponding to the dictionary
    '''
    namespace = Namespace()
    for key, value in dct.items():
        name = key.rstrip("_")
        if isinstance(value, dict) and not key.endswith("_"):
            setattr(namespace, name, dict_to_namespace(value))
        else:
            setattr(namespace, name, value)
    return namespace


def namespace_to_dict(ns):
    '''
    Transform a namespace to a dictionary
    :param ns: namespace to transform
    :return dictionary containing data in the namespace
    '''
    dct = vars(ns).copy()
    for key in dct:
        if isinstance(dct[key], Namespace):
            dct[key] = namespace_to_dict(dct[key])
    return dct


def run(cfg):
    '''
    Run the learning
    :param cfg: arguments for configuring the learning script
    :return the path to the directory where the results were stored
    '''
    # Initialize random number generator
    rng, _ = seeding.np_random(cfg.seed)

    # Initialize environment and agent
    if str.lower(cfg.task) == 'mdp':
        env = MDP(rng, cfg.env)
        agent = MDPAgent(env, rng, cfg.agent)
    elif str.lower(cfg.task) == 'mdp_v2':
        env = MDP_v2(rng, cfg.env)
        agent = MDPAgent_v2(env, rng, cfg.agent)
    elif str.lower(cfg.task) == 'smallmdp':
        env = SimpleMDP()
    elif str.lower(cfg.task) == 'pole':
        env = ContinuousCartPoleEnv()

    returns, grads, steps = [], [], []
    # returns = np.zeros((cfg.num_epochs, cfg.num_trajectories_return))
    # grads = np.zeros((cfg.num_epochs, cfg.num_trajectories, cfg.env.episode_length, cfg.env.num_actions * cfg.env.num_features))
    # steps = np.zeros(cfg.num_epochs * cfg.num_trajectories_return)
    # discounts = np.array([agent.gamma**step for step in range(cfg.env.episode_length)])
    # Run the simulation
    for ep in range(cfg.num_epochs):
        trajectories = []
        # trajectories = np.zeros((cfg.num_trajectories, cfg.env.episode_length, 3))
        env.reset()
        additional_ret = []
        # ret = np.zeros(cfg.num_trajectories_return)
        for t in range(cfg.num_trajectories_return):
            trajectory = []
            # trajectory = np.zeros((cfg.env.episode_length, 3))
            obs = env.get_state()
            rewards = []
            # rewards = np.zeros(cfg.env.episode_length)
            while True:
            # for step in range(cfg.env.episode_length + 1):
                action = agent.action(obs)
                new_obs, reward, done, _ = env.step(action)
                if done:
                    env.reset()
                    break
                # Add transition to the trajectory
                if t < cfg.num_trajectories:
                    trajectory.append((obs, action, reward))
                    # trajectory[step] = (obs, action, reward)
                rewards.append(reward)
                # rewards[step] = reward
                obs = new_obs
            if t < cfg.num_trajectories:
                trajectories.append(trajectory)
                # trajectories[t] = trajectory
            else:
                additional_ret.append(np.sum(np.array(rewards) * np.array([agent.gamma**step for step in range(len(rewards))])))
            # ret[t] = np.sum(rewards * discounts)
        # Optimize the agent
        ret, grad = agent.update(np.array(trajectories))
        # _, grad = agent.update(np.array(trajectories))
        returns.append(ret + additional_ret)
        grads.append(grad)
        steps.extend([ep] * cfg.num_trajectories_return)
        # returns[ep] = ret
        # grads[ep] = grad
        # steps[ep * cfg.num_trajectories_return: (ep + 1) * cfg.num_trajectories_return] = ep

    env.close()
    # print(returns)

    # Save data
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    results_dir = os.path.join('results', cfg.experiment, now)
    os.makedirs(results_dir)
    with open(os.path.join(results_dir, 'results.pkl'), 'wb') as f:
        data = {
            'returns': np.array(returns),
            'grads': np.array(grads),
            'env_settings': env.export_env(),
            'agent_params': agent.theta
        }
        pkl.dump(data, f)
    # Write configurations in the result directory
    with open(os.path.join(results_dir, 'config.yaml'), 'w') as f:
        yaml.dump(namespace_to_dict(cfg), f)

    # Plot
    sns.lineplot(steps, np.array(returns).flatten())
    plt.xlabel('Epoch')
    plt.ylabel('Avg return')
    plt.savefig(os.path.join(results_dir, 'plot'))

    return results_dir


if __name__ == '__main__':
    # Get configuration file
    argparser = ArgumentParser()
    argparser.add_argument('--config', type=str, default='zero_baseline',
            help='name of the config file to use for loading settings')
    args = argparser.parse_args()

    # Read configurations
    config_file = os.path.join('configs', args.config + '.yaml')
    if not os.path.exists(config_file):
        print(f'Config file {config_file} does not exist.')
        sys.exit(1)
    with open(config_file, 'r') as f:
        cfg = dict_to_namespace(yaml.load(f, Loader=yaml.SafeLoader))

    print(f'Started {args.config}')
    run(cfg)
    print(f'Finished {args.config}')
