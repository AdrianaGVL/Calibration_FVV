#######################
#  Created on: May 16, 2024
#  Author: Adriana GV
#######################

#!/bin/bash

# Paths
if ! command -v yq &>/dev/null; then
  echo "Error: 'yq' command not found. Please install yq"
  echo "Linux example: sudo apt-get install yq"
  echo "macOS example: brew install yq"
  exit 1
fi

config_file="./config_file.yml"

yq_v=$(yq --version 2>&1)
if [ "$yq_v" == "yq version 3.4.1" ]; then
    MAIN=$(yq r $config_file "working_path")
    SCENE=$MAIN/$(yq r $config_file "scene")
    frames_path=$SCENE/$(yq r $config_file 'frames_folder')
    depth_path=$SCENE/$(yq r $config_file 'depth_frames_folder')
    frames_to_move=$(yq r $config_file 'frames_to_rm')
else
    MAIN=$(yq e '.working_path' "$config_file")
    SCENE=$MAIN/$(yq e '.scene' "$config_file")
    frames_path=$SCENE/$(yq e '.frames_folder' "$config_file")
    depth_path=$SCENE/$(yq e '.depth_frames_folder' "$config_file")
    frames_to_move=$(yq e '.frames_to_rm' "$config_file")
fi

# removed_frames=$frames_path/not_used
# mkdir -p $removed_frames
depths=$(ls -t "$depth_path"/*.npy)
files=$(ls -t "$frames_path"/*.png)

# Counter
count=0
for file in $files; do
    if [ $count -eq $frames_to_move ]; then
        count=0
    else
        rm "$file" "$removed_frames/$(basename "$file")"
        echo "Removed: $(basename "$file")"
        count=$((count + 1))
    fi
done

# Counter
count=0
for depth in $depths; do
    if [ $count -eq $frames_to_move ]; then
        count=0
    else
        rm "$depth" "$removed_frames/$(basename "$depth")"
        echo "Removed: $(basename "$depth")"
        count=$((count + 1))
    fi
done