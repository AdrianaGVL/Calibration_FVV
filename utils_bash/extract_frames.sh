#!/bin/bash

#######################
#  Created on: May 16, 2024
#  Author: Adriana GV
#######################


# Config file path
dockers_path=$1
config_file=$2

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


python3 $dockers_path/Camera/images_svo.py --input_svo_file $VIDEO --input_config_file $config_file

chown -R $USER_ID:$GROUP_ID $SCENE