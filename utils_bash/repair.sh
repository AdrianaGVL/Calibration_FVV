#!/bin/bash

#######################
#  Created on: May 16, 2024
#  Author: Adriana GV
#######################

# Script for SVO2 Repearing files
# Config file path
config_file=$1

USER_ID=$(yq e '.user_id' "$config_file")
GROUP_ID=$(yq e '.user_group' "$config_file")

#Paths
yq_v=$(yq --version 2>&1)
if [ "$yq_v" == "yq version 3.4.1" ]; then
    MAIN=$(yq r $config_file "working_path")
    SCENE=$MAIN/$(yq r $config_file "scene")
    VIDEO=$SCENE/$(yq r $config_file "svo_file")
else
    MAIN=$(yq e '.working_path' "$config_file")
    SCENE=$MAIN/$(yq e '.scene' "$config_file")
    VIDEO=$SCENE/$(yq e '.svo_file' "$config_file")
fi

# Repair video in any case
cd /usr/local/zed/tools
./ZED_SVO_Editor -repair $VIDEO

chown -R $USER_ID:$GROUP_ID $VIDEO