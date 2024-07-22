#!/bin/bash

#######################
#  Created on: May 16, 2024
#  Author: Adriana GV
#######################

# Script for SVO2 Repearing files
# Config file path
config_file=$1

yq_v=$(yq --version 2>&1)
if [ "$yq_v" == "yq version 3.4.1" ]; then
    MAIN=$(yq r $config_file "working_path")
    SCENE=$MAIN/$(yq r $config_file "scene")
else
    MAIN=$(yq e '.working_path' "$config_file")
    SCENE=$MAIN/$(yq e '.scene' "$config_file")
fi

# Repair video in any case
for VIDEO in $SCENE/*.{svo2,svo}; do
    if [ -f "$VIDEO" ]; then
        cd /usr/local/zed/tools
        ./ZED_SVO_Editor -repair $VIDEO
    fi
done
