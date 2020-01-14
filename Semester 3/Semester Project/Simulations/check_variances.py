import numpy as np
import pandas as pd
import pickle as pkl
from collections import defaultdict
from argparse import ArgumentParser


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--file', type=str, help='path to the file containing the variances')
    args = argparser.parse_args()

    # Read variances
    with open(args.file, 'rb') as f:
        df = pkl.load(f)

    # Check variance improvement when using optimal baseline
    const_baseline_var, state_baseline_var = defaultdict(int), defaultdict(int)
    const_baseline_sum_var, state_baseline_sum_var = defaultdict(int), defaultdict(int)
    for i in range(len(df)):
        # Check the total variance
        # Check constant baseline
        const_val = np.all(df.loc[i]['average'] > df.loc[i]['optimal_const'])
        const_baseline_var['all_better'] += const_val
        const_baseline_var['part_better'] += 1 - const_val
        const_baseline_var['most_better'] += (np.sum(df.loc[i]['average'] > df.loc[i]['optimal_const']) > len(df.iloc[i]['average']) / 2)
        # Check state dependent baseline
        state_val = np.all(df.loc[i]['state'] > df.loc[i]['optimal_state'])
        state_baseline_var['all_better'] += state_val
        state_baseline_var['part_better'] += 1 - state_val
        state_baseline_var['most_better'] += (np.sum(df.loc[i]['state'] > df.loc[i]['optimal_state']) > len(df.iloc[i]['state']) / 2)

        # Check the sum of variances
        # Check constant baseline
        const_val = np.all(df.loc[i]['sum_average'] > df.loc[i]['sum_optimal_const'])
        const_baseline_sum_var['all_better'] += const_val
        const_baseline_sum_var['part_better'] += 1 - const_val
        const_baseline_sum_var['most_better'] += (np.sum(df.loc[i]['sum_average'] > df.loc[i]['sum_optimal_const']) > np.prod(df.iloc[i]['sum_average'].shape) / 2)
        # Check state dependent baseline
        state_val = np.all(df.loc[i]['sum_state'] > df.loc[i]['sum_optimal_state'])
        state_baseline_sum_var['all_better'] += state_val
        state_baseline_sum_var['part_better'] += 1 - state_val
        state_baseline_sum_var['most_better'] += (np.sum(df.loc[i]['sum_state'] > df.loc[i]['sum_optimal_state']) > np.prod(df.iloc[i]['sum_state'].shape) / 2)

    print('Total variance')
    print('  Constant baseline')
    print(f"    All better:\t\t{const_baseline_var['all_better']}\tout of {len(df)}")
    print(f"    Part better:\t{const_baseline_var['part_better']}\tout of {len(df)}")
    print(f"    Most better:\t{const_baseline_var['most_better']}\tout of {len(df)}")
    print('  State baseline')
    print(f"    All better:\t\t{state_baseline_var['all_better']}\tout of {len(df)}")
    print(f"    Part better:\t{state_baseline_var['part_better']}\tout of {len(df)}")
    print(f"    Most better:\t{state_baseline_var['most_better']}\tout of {len(df)}")
    print()
    print('Sum of variances')
    print('  Constant baseline')
    print(f"    All better:\t\t{const_baseline_sum_var['all_better']}\tout of {len(df)}")
    print(f"    Part better:\t{const_baseline_sum_var['part_better']}\tout of {len(df)}")
    print(f"    Most better:\t{const_baseline_sum_var['most_better']}\tout of {len(df)}")
    print('  State baseline')
    print(f"    All better:\t\t{state_baseline_sum_var['all_better']}\tout of {len(df)}")
    print(f"    Part better:\t{state_baseline_sum_var['part_better']}\tout of {len(df)}")
    print(f"    Most better:\t{state_baseline_sum_var['most_better']}\tout of {len(df)}")
