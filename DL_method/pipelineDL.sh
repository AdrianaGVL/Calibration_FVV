#!/bin/bash

#######################
#  Created on: June 14, 2024
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
config_file="config_DL.yml"
dockers_path="dataset/prueba"
not_dockers_path="/home/agv/ZED/prueba"
MAIN=$(yq r $config_file "working_path")
SCENE=$MAIN/$(yq r $config_file "scene")
OUTPUT=$SCENE/$(yq e '.out_path' "$config_file")
MATCHES_DIR=$OUTPUT/$(yq e '.out_path' "$config_file")
DIM_PATH=$(yq r $config_file "dim_path")
MY_SDK_PATH=(yq r $config_file "my_sdk")

# Options
matches_software_=superpoint+superglue

docker run -d -it --name OPENMVG --rm -v /home/agv/ZED/:/dataset/ --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 openmvg
docker exec OPENMVG apt-get install wget
docker exec OPENMVG apt-get install jq -y
docker exec OPENMVG wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq &&\
docker exec OPENMVG chmod +x /usr/bin/yq

yq w -i $config_file "user_id" $(id -u) && \
yq w -i $config_file "user_group" $(id -g) && \

USER_ID=$(yq e '.user_id' "$config_file")
GROUP_ID=$(yq e '.user_group' "$config_file")

# MUST RUN IN THE DIM DIRECTORY
cd $DIM_PATH
python main.py --dir $MAIN/$SCENE/$DATASET --pipeline $matches_software --quality highest && \
cd $MY_SDK_PATH
mv $MAIN/$SCENE/results_*/ $MAIN/$SCENE/feats_matches_dim/
pyhton3 DL_method/DIM2MVG.py && \
yq w -i $config_file "working_path" $dockers_path && \
docker exec OPENMVG bash ./dataset/Calibration_FVV/OpenMVG/DIM.sh ;
yq w -i $config_file "working_path" $not_dockers_path && \
mkdir $MAIN/$SCENE/$DATASET/not_floor
mkdir $MAIN/$SCENE/$MATCHES_DIR/not_floor
mv $MAIN/$SCENE/$DATASET/colour_* $MAIN/$SCENE/$DATASET/not_floor/colour_*
mv $MAIN/$SCENE/$MATCHES_DIR/colour_* $MAIN/$SCENE/$MATCHES_DIR/not_floor/colour_*
yq w -i $config_file "working_path" $dockers_path && \
docker exec OPENMVG bash ./dataset/Calibration_FVV/OpenMVG/DIM_known.sh ;
yq w -i $config_file "working_path" $not_dockers_path && \
echo 'Error study: 1. Plane 3D:' && \
python3 Error_study/plane3D.py && \
echo 'Error study: 2. Scale Factor:' && \
python3 DL_method/scale.py && \
echo 'Error study: 3. Scene Rescale:' && \
python3 Error_study/rescale.py && \
echo 'Extrinsics generation' && \
python3 extrinsic_floor.py

yq w -i $config_file "user_id" 0
yq w -i $config_file "user_group" 0

docker stop OPENMVG