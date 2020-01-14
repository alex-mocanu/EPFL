import os
import sys
import yaml
import numpy as np
import pickle as pkl
from gym.utils import seeding
from collections import defaultdict
from argparse import ArgumentParser, Namespace

from envs.MDP import MDP
from agents.agent import MDPAgent
from agents.baselines import get_baseline, generate_trajectories


def dict_to_namespace(dct):
    namespace = Namespace()
    for key, value in dct.items():
        name = key.rstrip("_")
        if isinstance(value, dict) and not key.endswith("_"):
            setattr(namespace, name, dict_to_namespace(value))
        else:
            setattr(namespace, name, value)
    return namespace


def load_env(env_settings, rng, cfg):
    '''
    Generates an MDP environment and sets its parameters
    :param env_settings: environment paramets
    :return MDP environment
    '''
    env = MDP(rng, cfg)
    env.import_env(env_settings)
    return env


def load_agents(agent_params, env, rng, cfg):
    '''
    Generates agents with various baseline types
    :param env: environment with which the agent interacts
    :param agent_params: agent parameters
    :return MDP agents
    '''
    baseline_types = ['zero', 'average', 'state', 'optimal_const', 'optimal_state']
    # Generate agents with all baselines
    agents = {}
    for baseline_type in baseline_types:
        cfg.baseline.type = baseline_type
        agent = MDPAgent(env, rng, cfg)
        agent.set_parameters(agent_params)
        agents[baseline_type] = agent
    return agents


def compute_variances(args, rng, exact_variance):
    '''
    Computes the total variance and the sum of individual variances
    :param args: parameters for getting data and running the computation
    :param rng: random number generator used for running the environment and the agent
    :param exact_variance: whether or not to compute the exact expressions for the total variance and sum of variances
    :return the total variance and the sum of individual variances
    '''
    param_file = os.path.join(args.param_dir, 'results.pkl')
    config_file = os.path.join(args.param_dir, 'config.yaml')
    if not os.path.exists(param_file):
        print('Invalid parameter directory')
        sys.exit(1)
    with open(param_file, 'rb') as f:
        data = pkl.load(f)
    with open(config_file, 'r') as f:
        cfg = dict_to_namespace(yaml.load(f, Loader=yaml.SafeLoader))

    # Load environment and agents
    env = load_env(data['env_settings'], rng, cfg.env)
    agents = load_agents(np.zeros_like(data['agent_params']), env, rng, cfg.agent)

    # Collect trajectories for the given policy
    trajectories, probs = [], []
    if exact_variance:
        trajs = []
        for init_state in range(env.num_states):
            generate_trajectories(env, agents['zero'], init_state, env.episode_length, [], 1 / env.num_states, trajs)
        trajectories = [t[0] for t in trajs]
        probs = [t[1] for t in trajs]
    else:
        for _ in range(args.num_trajectories):
            env.reset()
            obs = env.get_state()
            trajectory = []
            while True:
                action = agents['zero'].action(obs)
                new_obs, reward, done, _ = env.step(action)
                if done:
                    env.reset()
                    break
                trajectory.append((obs, action, reward))
                obs = new_obs
            trajectories.append(trajectory)
        probs = np.ones(args.num_trajectories) / args.num_trajectories

    trajectories = np.array(trajectories)

    # Compute gradient estimations for each agent
    step_variances, variances = {}, {}
    for agent_type in agents:
        _, grads = agents[agent_type].update(trajectories)
        # Compute the variance for the whole gradient
        sum_grads = grads.sum(axis=1)
        variances[agent_type] = np.average((sum_grads - np.average(sum_grads, axis=0, weights=probs))**2, axis=0, weights=probs)
        # Compute the variances of each timestep
        step_variances[agent_type] = np.average((grads - np.average(grads, axis=0, weights=probs))**2, axis=0, weights=probs)

    return variances, step_variances


def run(args):
    '''
    Run the task of computing variances
    :param args: arguments used for configuring the script
    :return the total variance and sum of individual variances
    '''
    variances, step_variances = defaultdict(list), defaultdict(list)
    for seed in range(args.seed):
        # Set random number generator
        rng, _ = seeding.np_random(seed)
        var, step_var = compute_variances(args, rng, args.exact_variance)
        for agent_type in var:
            variances[agent_type].append(var[agent_type])
            step_variances[agent_type].append(step_var[agent_type])

    for agent_type in variances:
        variances[agent_type] = np.mean(np.array(variances[agent_type]), axis=0)
    for agent_type in variances:
        step_variances[agent_type] = np.mean(np.array(step_variances[agent_type]), axis=0)

    if args.print:
        print('Variances')
        for agent_type in variances:
            print(f'{agent_type}: {variances[agent_type]}')
        print()
        print('Sum of variances over timesteps')
        for agent_type in variances:
            print(f'{agent_type}: {step_variances[agent_type]}')

    return variances, step_variances


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--param_dir', type=str,
        help='directory containing the parameters for the env and the agent')
    argparser.add_argument('--num_trajectories', type=int, default=1000,
        help='number of trajectories to collect to evaluate the variances')
    argparser.add_argument('--exact_variance', type=int, default=0,
        help='whether to compute the true variances or estimations')
    argparser.add_argument('--seed', type=int, default=1,
        help='number of random seeds')
    argparser.add_argument('--print', type=int, default=1,
        help='whether or not to print the results')
    args = argparser.parse_args()

    run(args)
