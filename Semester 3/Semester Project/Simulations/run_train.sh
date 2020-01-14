#!/bin/bash

configs=(zero_baseline average_baseline state_baseline optimal_const_baseline optimal_state_baseline)

if [ $1 == all ]; then
    for config in ${configs[@]}; do
        time python main.py --config $config &
    done
else
    time python main.py --config $1
fi
