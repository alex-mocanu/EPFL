import os
import yaml
import shutil
import pandas as pd
import pickle as pkl
from collections import defaultdict
from argparse import ArgumentParser, Namespace

import main
import variance_comparison


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--num_seeds', type=int, default=10, help='number of random seeds used for generating \
        environments')
    argparser.add_argument('--num_seeds_variance', type=int, default=1, help='number of random seeds used for \
        evaluating variances')
    argparser.add_argument('--exact_baseline', type=int, default=0, help='whether to compute exact baseline values \
        when evaluating variances')
    argparser.add_argument('--exact_variance', type=int, default=0, help='whether to compute exact variance values')
    argparser.add_argument('--num_states', type=int, default=3, help='number of states in the environment')
    argparser.add_argument('--num_actions', type=int, default=3, help='number of actions of the agent')
    argparser.add_argument('--episode_length', type=int, default=5, help='length of an episode in the game')
    args = argparser.parse_args()

    res_file = f'results/variance_eval/all_var_init_param_{args.num_states}_{args.num_actions}_{args.episode_length}_{args.exact_variance}_{args.exact_baseline}.pkl'

    # Read configurations
    config_file = 'configs/no_baseline.yaml'
    with open(config_file, 'r') as f:
        cfg = main.dict_to_namespace(yaml.load(f, Loader=yaml.SafeLoader))
        cfg.env.num_states = args.num_states
        cfg.env.num_actions = args.num_actions
        cfg.env.episode_length = args.episode_length

    var_cols = ['zero', 'average', 'state', 'optimal_const', 'optimal_state']
    sum_var_cols = [f'sum_{col}' for col in var_cols]
    df_cols = var_cols + sum_var_cols
    df = pd.DataFrame(columns=df_cols)
    # Generate different environments to run experiments
    for seed in range(args.num_seeds):
        cfg.seed = seed
        # Run training
        param_dir = main.run(cfg)
        # Write new setting in the configuration file from the results directory
        cfg.agent.baseline.exact = (args.exact_baseline != 0)
        with open(os.path.join(param_dir, 'config.yaml'), 'w') as f:
            yaml.dump(main.namespace_to_dict(cfg), f)
        # Prepare parameters for variance computation
        variance_args = main.dict_to_namespace({
            'param_dir': param_dir,
            'num_trajectories': 1000,
            'exact_variance': args.exact_variance,
            'seed': args.num_seeds_variance,
            'print': 0
        })
        # Run variance evaluation
        variances, sum_variances = variance_comparison.run(variance_args)
        # Remove results directory
        shutil.rmtree(param_dir)
        # Collect results
        res = []
        for key in var_cols:
            res.append(variances[key])
        for key in var_cols:
            res.append(sum_variances[key])
        df = df.append({df_cols[i]:res[i] for i in range(len(df_cols))}, ignore_index=True)
        with open(res_file, 'wb') as f:
            pkl.dump(df, f)
        print(f'Finished seed {seed}')
