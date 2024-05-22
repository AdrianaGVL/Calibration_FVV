#######################
#  Script for copy 6144 bytes OpenMVG .desc files
#  Created on: March 18, 2024
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

config_file="../config_file.yml"

MAIN=$(yq e '.working_path' "$config_file")
SCENE=$MAIN/$(yq e '.scene' "$config_file")
OUTPUT=$SCENE/$(yq e '.out_path' "$config_file")
MATCHES=$OUTPUT'/matches'
MYMATCHES=$OUTPUT/matches_for_known

# Bytes needed
num_corners_x=$(yq e '.num_corners_x' "$config_file")
num_corners_y=$(yq e '.num_corners_y' "$config_file")
bytes_per_corner=$(yq e '.length_unit' "$config_file")
num_corners=$(($num_corners_x * $num_corners_y))
num_bytes=$(($bytes_per_corner * $num_corners))

# Loop through files in the target directory
for file in "$MATCHES"/*".desc"; do
  if [ -f "$file" ]; then
  	base_name=$(basename ${file})
	  echo $base_name
    { head -c$num_bytes > "$MYMATCHES/$base_name"; } < $file
  fi
done