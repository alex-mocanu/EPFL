#!/bin/bash

if [ $1 == all ]; then
    dirs=(mdp_zero_baseline mdp_average_baseline mdp_state_baseline mdp_optimal_const_baseline mdp_optimal_state_baseline)
    for dir in ${dirs[@]}; do
        rm -r ~/Desktop/EPFL/Semester\ 3/Semester\ Project/Simulations/results/$dir/*
    done
elif [ -f $1 ]; then
    rm -r $1/*
else
    echo Invalid command
fi
