#!/bin/bash

#######################
#  Created on: June 6, 2024
#  Author: Adriana GV
#######################

# Paths
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

config_file="config_file.yml"
dockers_path="dataset/suelo_127"
not_dockers_path="/home/agv/ZED/suelo_127"
MAIN=$(yq r $config_file "working_path")

ZED_SDK_V='v3'

if [ "$ZED_SDK_V" == 'v4' ]; then
  docker run -d -it --name ZED --rm -v /home/agv/ZED/:/ZED/ --gpus all -e NVIDIA_DRIVER_CAPABILITIES=video,compute,utility --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 zed_sdk_v4
fi

docker run -d -it --name OPENMVG --rm -v /home/agv/ZED/:/dataset/ --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 openmvg
docker exec OPENMVG apt-get install wget
docker exec OPENMVG apt-get install jq -y
docker exec OPENMVG wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq &&\
docker exec OPENMVG chmod +x /usr/bin/yq

yq w -i $config_file "user_id" $(id -u) && \
yq w -i $config_file "user_group" $(id -g) && \
echo 'Working directory: '$MAIN

scene_name=$(basename ${SCENE})
echo 'Scene under study: '$scene_name
yq w -i $config_file "scene" $scene_name && \

if [ "$ZED_SDK_V" == "v4" ]; then
yq w -i $config_file "working_path" $dockers_path && \
docker exec ZED bash ./ZED/Calibration_FVV/utils_bash/repair.sh && \
docker exec ZED bash ./ZED/Calibration_FVV/utils_bash/extract_frames.sh ;
docker exec OPENMVG bash ./ZED/Calibration_FVV/OpenMVG/ZED2.sh ;
yq w -i $config_file "working_path" $not_dockers_path
else
./utils_bash/extract_frames_e.sh ;
yq w -i $config_file "working_path" $dockers_path && \
docker exec OPENMVG bash ./dataset/Calibration_FVV/OpenMVG/poses.sh ;
yq w -i $config_file "working_path" $not_dockers_path
fi && \
echo 'Corner Extraction' && \
python3 OpenCV/corners_feat_file.py && \
echo 'Descriptors Generation' && \
./utils_bash/copy_desc.sh && \
echo 'Matches Computation' && \
python3 OpenCV/matches.py && \
echo 'Reconstruction from Known Poses' && \
yq w -i $config_file "working_path" $dockers_path && \
docker exec OPENMVG bash ./dataset/Calibration_FVV/OpenMVG/poses_Known.sh ;
yq w -i $config_file "working_path" $not_dockers_path && \
echo 'Error study: 1. Plane 3D:' && \
python3 Error_study/plane3D.py && \
echo 'Error study: 2. Scale Factor:' && \
python3 Error_study/scale.py && \
echo 'Error study: 3. Scene Rescale:' && \
python3 Error_study/rescale.py && \
echo 'Obtaining poses with respect to the floor'
python3 Error_study/extrinsic_floor.py

yq w -i $config_file "user_id" 0
yq w -i $config_file "user_group" 0

if [ "$ZED_SDK_V" == "v4" ]; then
  docker stop ZED
fi

docker stop OPENMVG