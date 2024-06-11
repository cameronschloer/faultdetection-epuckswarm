#!/bin/bash

# Makes 30 argos files for each possible task and fault

SEED=0
TASK_TYPES=("SWARM_AGGREGATION" "SWARM_DISPERSION" "SWARM_FLOCKING" "SWARM_HOMING" "SWARM_FORAGING")
FAULT_TYPES=("FAULT_PROXIMITYSENSORS_SETMIN" "FAULT_PROXIMITYSENSORS_SETMAX" "FAULT_PROXIMITYSENSORS_SETRANDOM" "FAULT_RABSENSOR_SETOFFSET" "FAULT_ACTUATOR_LWHEEL_SETZERO" "FAULT_ACTUATOR_RWHEEL_SETZERO" "FAULT_ACTUATOR_BWHEELS_SETZERO")

for (( i=0; i < ${#TASK_TYPES[@]}; i++ ))
do
    for (( j = 0; j < ${#FAULT_TYPES[@]}; j++ ))
    do
        for (( k = 0; k < 30; k ++ ))
        do
            SEED=$(($SEED + 1))

            if [ ${TASK_TYPES[i]} == "SWARM_FORAGING" ]
            then
                python3 experiments/generate_experiments.py -- ${FAULT_TYPES[i]} $SEED --length=245 --led_bins=2 --lower=450 --upper=1250
            else
                python3 experiments/generate_hom.py $SEED --length=600 --id_of_faulty=15 ${TASK_TYPES[i]} ${FAULT_TYPES[j]}
            fi
        done
    done
done
