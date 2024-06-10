#!/bin/bash

# Makes 30 argos files for each possible task and fault

SEED=0
TASK_TYPES=("SWARM_AGGREGATION" "SWARM_DISPERSION" "SWARM_FLOCKING" "SWARM_HOMING")
FAULT_TYPES=("FAULT_PROXIMITYSENSORS_SETMIN" "FAULT_PROXIMITYSENSORS_SETMAX" "FAULT_PROXIMITYSENSORS_SETRANDOM" "FAULT_RABSENSOR_SETOFFSET" "FAULT_ACTUATOR_LWHEEL_SETZERO" "FAULT_ACTUATOR_RWHEEL_SETZERO" "FAULT_ACTUATOR_BWHEELS_SETZERO")

for (( i=0; i < ${#TASK_TYPES[@]}; i++ ))
do
    for (( j = 0; j < ${#FAULT_TYPES[@]}; j++ ))
    do
        for (( k = 0; k < 30; k ++ ))
        do
            SEED=$(($SEED + 1))
            python3 experiments/generate_hom.py $SEED --length=600 --id_of_faulty=15 ${TASK_TYPES[i]} ${FAULT_TYPES[j]}
            argos3 -z -c experiments/hom_experiments/${TASK_TYPES[i]}/${FAULT_TYPES[j]}/epuck_${TASK_TYPES[i]}_${FAULT_TYPES[j]}_$SEED.argos 
        done
    done
done
