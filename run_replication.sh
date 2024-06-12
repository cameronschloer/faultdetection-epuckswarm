#!/bin/bash

task=${1:-'null'}
fault=${2:-'null'}

if [[ $task == 'null' ]]; then
    exp_dir="experiments/replication_experiments"
    data_dir="data/replication_data"
    dir_ls=($exp_dir $data_dir)

    for dir in ${dir_ls[@]}; do
        for task_dir in "$dir"/*; do
            for fault_dir in "$task_dir"/*; do
                for file in "$fault_dir"/*; do
                    if [[ -f "$file" ]]; then
                        if [[ "${file##*.}" == "argos" ]]; then
                            argos3 -z -c $file
                        elif [[ "${file##*.}" == "txt" ]]; then
                            python3 analysis/analyze_replication_data.py $file
                        fi
                    fi
                done
            done
        done
    done
elif [[ $fault == 'null' ]]; then
    exp_dir="experiments/replication_experiments/$task"
    data_dir="data/replication_data/$task"
    dir_ls=($exp_dir $data_dir)

    for task_dir in ${dir_ls[@]}; do
        for fault_dir in "$task_dir"/*; do
            for file in "$fault_dir"/*; do
                if [[ -f "$file" ]]; then
                    if [[ "${file##*.}" == "argos" ]]; then
                        argos3 -z -c $file
                    elif [[ "${file##*.}" == "txt" ]]; then
                        python3 analysis/analyze_replication_data.py $file
                    fi
                fi
            done
        done
    done
else
    exp_dir="experiments/replication_experiments/$task/$fault"
    data_dir="data/replication_data/$task/$fault"
    dir_ls=($exp_dir $data_dir)

    for fault_dir in ${dir_ls[@]}; do
        for file in "$fault_dir"/*; do
            if [[ -f "$file" ]]; then
                if [[ "${file##*.}" == "argos" ]]; then
                    argos3 -z -c $file
                elif [[ "${file##*.}" == "txt" ]]; then
                    python3 analysis/analyze_replication_data.py $file
                fi
            fi
        done
    done
fi