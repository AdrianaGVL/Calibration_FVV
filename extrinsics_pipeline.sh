#!/bin/bash

#######################
#  Created on: June 6, 2024
#  Author: Adriana GV
#######################

# Requiered libraries?
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
config_file=$1
configs=$(dirname "$config_file")
new_config_file=$configs/config.yml
working_code=$(basename $(pwd))
MAIN=$(yq r $config_file "device_path")
dockers_path=$(yq r $config_file "dockers_path")
SCENE=$(yq r $config_file "scene")
# Config file for code
cat $config_file > $new_config_file
config_file=$new_config_file


ZED_SDK_V='v3'

if [ "$ZED_SDK_V" == 'v4' ]; then
  docker run -d -it --name ZED --rm -v $(yq r $config_file "device_path")/:/$(yq r $config_file "dockers_path")/ --gpus all -e NVIDIA_DRIVER_CAPABILITIES=video,compute,utility --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 zed_sdk_v4
fi

docker run -d -it --name OPENMVG --rm -v $(yq r $config_file "device_path")/:/$(yq r $config_file "dockers_path")/ --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 openmvg
docker exec OPENMVG apt-get install wget
docker exec OPENMVG apt-get install jq -y
docker exec OPENMVG wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq &&\
docker exec OPENMVG chmod +x /usr/bin/yq

yq w -i $config_file "user_id" $(id -u) && \
yq w -i $config_file "user_group" $(id -g) && \

yq w -i $config_file "working_path" $MAIN && \
echo 'Working directory: '$MAIN

if [ "$ZED_SDK_V" == "v4" ]; then
  yq w -i $config_file "working_path" $dockers_path && \
  docker exec ZED bash ./$dockers_path/$working_code/utils_bash/repair.sh /$dockers_path/$working_code/$config_file && \
  docker exec ZED bash ./$dockers_path/$working_code/utils_bash/extract_frames_e.sh /$dockers_path/$working_code/$config_file ;
  docker exec OPENMVG bash ./$dockers_path/$working_code/OpenMVG/poses.sh /$dockers_path/$working_code/$config_file ;
  yq w -i $config_file "working_path" $not_dockers_path
else
  ./utils_bash/extract_frames_e.sh $(pwd)/$config_file ;
  yq w -i $config_file "working_path" $dockers_path/$(yq r $config_file "camera")_$(yq r $config_file "serial_num") && \
  docker exec OPENMVG bash ./$dockers_path/$working_code/OpenMVG/poses.sh /$dockers_path/$working_code/$config_file ;
  yq w -i $config_file "working_path" $MAIN/$(yq r $config_file "camera")_$(yq r $config_file "serial_num")
fi && \
echo 'Corner Extraction' && \
python3 OpenCV/corners_feat_file.py $(pwd)/$config_file && \
echo 'Descriptors Generation' && \
./utils_bash/copy_desc.sh $(pwd)/$config_file && \
echo 'Matches Computation' && \
python3 OpenCV/matches.py $(pwd)/$config_file && \
echo 'Reconstruction from Known Poses' && \
yq w -i $config_file "working_path" $dockers_path/$(yq r $config_file "camera")_$(yq r $config_file "serial_num") && \
docker exec OPENMVG bash ./$dockers_path/$working_code/OpenMVG/poses_known.sh /$dockers_path/$working_code/$config_file ;
yq w -i $config_file "working_path" $MAIN/$(yq r $config_file "camera")_$(yq r $config_file "serial_num") && \
echo 'Error study: 1. Plane 3D:' && \
python3 Error_study/plane3D.py $(pwd)/$config_file && \
echo 'Error study: 2. Scale Factor:' && \
python3 Error_study/scale.py $(pwd)/$config_file && \
echo 'Error study: 3. Scene Rescale:' && \
python3 Error_study/rescale.py $(pwd)/$config_file && \
echo 'Obtaining poses with respect to the floor'
python3 utils_py/extrinsic_floor.py $(pwd)/$config_file

yq w -i $config_file "user_id" 0
yq w -i $config_file "user_group" 0

if [ "$ZED_SDK_V" == "v4" ]; then
  docker stop ZED
fi

docker stop OPENMVG