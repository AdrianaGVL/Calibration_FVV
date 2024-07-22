#!/bin/bash

#######################
#  Created on: March 18, 2024
#  Author: Adriana GV
#######################

#!/bin/bash

# Libraries
# YAML
if ! command -v yq &>/dev/null; then
  echo "Error: 'yq' command not found. Please install yq"
  echo "Linux example: sudo apt-get install yq"
  echo "macOS example: brew install yq"
  exit 1
fi

# Config file
config_file=$1

# Paths
MAIN=$(yq r $config_file "working_path")
SCENE=$MAIN/$(yq r $config_file "scene")
OUTPUT=$SCENE/$(yq r $config_file "out_path")
MATCHES=$OUTPUT'/matches'
MYMATCHES=$OUTPUT/matches_for_known

# Bytes needed
num_corners_x=$(yq r $config_file "num_corners_x" )
num_corners_y=$(yq r $config_file "num_corners_y")
bytes_per_corner=$(yq r $config_file "length_unit")
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