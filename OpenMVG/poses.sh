#!/bin/bash

#######################
#  Created on: June 7, 2024
#  Author: Adriana GV
#######################


# Libraries
# YAML
if ! command -v yq &>/dev/null; then
  echo "Error: 'yq' command not found. Please install yq"
  echo "Linux example: sudo apt-get install yq"
  echo "macOS example: brew install yq"
  exit 1
fi
# JSON
if ! command -v jq &>/dev/null; then
  echo "Error: 'jq' command not found. Please install jq"
  echo "Linux example: sudo apt-get install jq"
  echo "macOS example: brew install jq"
  exit 1
fi

# Paths
# config_file="/dataset/Calibration_FVV/config_file.yml"
config_file=$1

USER_ID=$(yq e '.user_id' "$config_file")
GROUP_ID=$(yq e '.user_group' "$config_file")

MAIN=$(yq e '.working_path' "$config_file")
SCENE=$MAIN/$(yq e '.scene' "$config_file")
DATASET=$SCENE/$(yq e '.frames_folder' "$config_file")
images_list=$DATASET/$(yq e '.image_list' "$config_file")
OUTPUT=$SCENE/$(yq e '.out_path' "$config_file")
mkdir -p $OUTPUT
MATCHES=$OUTPUT'/matches'
mkdir -p $MATCHES
RECONSTRUCTION=$OUTPUT/Reconstruction
mkdir -p $RECONSTRUCTION

mv $images_list $OUTPUT/lists.txt

# openMVG Execution
# 1. File txt to sfm_data
echo '1. Converting files list to sfm_data'
openMVG_main_ConvertList -i $DATASET -o $OUTPUT -c 1 -g 0

mv $OUTPUT/sfm_data.json $OUTPUT/sfm_data_no_poses.json

# 2. Features Computation
echo '2. Executing Features Computation'
openMVG_main_ComputeFeatures -i $OUTPUT/sfm_data_no_poses.json -o $MATCHES -m SIFT -f 1 -p ULTRA -n 8

# 3. Pair Generator
echo '3. Executing Pair Generator'
openMVG_main_PairGenerator -i $OUTPUT/sfm_data_no_poses.json -o $MATCHES/pairs.bin -m EXHAUSTIVE

# 4. Matches Computation
echo '4. Executing Matches Computation'
openMVG_main_ComputeMatches -i $OUTPUT/sfm_data_no_poses.json -o $MATCHES/matches.putative.bin -p $MATCHES/pairs.bin -n AUTO

# 5. Geometric Filtering
echo '5. Executing Geometric Filtering'
openMVG_main_GeometricFilter -i $OUTPUT/sfm_data_no_poses.json -m $MATCHES/matches.putative.bin -o $MATCHES/matches.f.bin -p $MATCHES/pairs.bin

# 6. Compute Structure from Motion
echo '6. Executing Strucuture from Motion'
openMVG_main_SfM -i $OUTPUT/sfm_data_no_poses.json -m $MATCHES -o $RECONSTRUCTION -s GLOBAL -M $MATCHES/matches.f.bin

# 7. New SfM data conversion to JSON
echo '7. Executing SfM data conversion to JSON'
openMVG_main_ConvertSfM_DataFormat -i $RECONSTRUCTION/sfm_data.bin -o $RECONSTRUCTION/sfm_data.json

mv $RECONSTRUCTION/sfm_data.json $OUTPUT/sfm_data.json

# Give access out of the docker
chown -R $USER_ID:$GROUP_ID $OUTPUT
chown -R $USER_ID:$GROUP_ID $MATCHES
chown -R $USER_ID:$GROUP_ID $RECONSTRUCTION