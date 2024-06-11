#!/bin/bash

task=${1:-'null'}
fault=${2:-'null'}

if [[ $task == 'null' ]]; then
    dir="experiments/replication_experiments"
    for task_dir in "$dir"/*
    do
        for fault_dir in "$task_dir"/*
        do
            for test_file in "$fault_dir"/*
            do
                if [[ -f "$test_file" ]]
                then
                    argos3 -z -c $test_file
                fi
            done
        done
    done
elif [[ $fault == 'null' ]]; then
    task_dir="experiments/replication_experiments/$task"
    for fault_dir in "$task_dir"/*
    do
        for test_file in "$fault_dir"/*
        do
            if [[ -f "$test_file" ]]; then
                argos3 -z -c $test_file
            fi
        done
    done
else
    fault_dir="experiments/replication_experiments/$task/$fault"
    for test_file in "$fault_dir"/*
    do
        if [[ -f "$test_file" ]]; then
            argos3 -z -c $test_file
        fi
    done
fi