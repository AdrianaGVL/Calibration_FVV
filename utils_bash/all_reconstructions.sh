#######################
#  Created on: May 17, 2024
#  Author: Adriana GV
#######################


# Script for execute all the reconstructions
# Run in docker: ./dataset/extract_frames.sh

# Paths
if ! command -v yq &>/dev/null; then
  echo "Error: 'yq' command not found. Please install yq"
  echo "Linux example: sudo apt-get install yq"
  echo "macOS example: brew install yq"
  exit 1
fi

config_file="../config_file.yml"



MAIN=$(yq e '.working_path' "$config_file")

for SCENE in "$MAIN"/*/; do
  ./dataset/ZED2.sh $SCENE
done