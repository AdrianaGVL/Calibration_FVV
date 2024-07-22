#!/bin/bash

# Pipeline for chessboard recosntruction

# Check the integrity of the videos
# Extract frames from the videos
# Remove 1 frame every other one (Resource problems, RAM)
# Execute openMVG to obtain intrinsics and poses
# Generate the features files
# Generate the new descriptors files
# Generate the pairs file and the matching one
# Execute the reconstruction from known poses
# Analyse if reconstruction make sense (every point shoul be in the same plane)
# Rescale the scene so depth can be compare
# Some more metrics are obtained
# Depth comparison
# Errors comparison

## IF yq version is 4 or higher change yq commands:
# WRITE: $(yq -i '.working_path = "$MAIN"' "$config_file")
# READ: $(yq e '.scene' "$config_file")

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
for SCENE in $MAIN/*.{svo2,svo}; do
  if [ -f "$SCENE" ]; then
    scene_name=$(basename ${SCENE})
    echo 'Scene under study: '$scene_name
    if [ "$ZED_SDK_V" == "v4" ]; then
      yq w -i $config_file "working_path" $dockers_path && \
      docker exec ZED bash ./$dockers_path/Calibration_FVV/utils_bash/repair.sh && \
      docker exec ZED bash ./$dockers_path/Calibration_FVV/utils_bash/extract_frames.sh ;
      docker exec OPENMVG bash ./$dockers_path/Calibration_FVV/OpenMVG/camera.sh /$dockers_path/$working_code/$config_file ;
      yq w -i $config_file "working_path" $MAIN/$(yq r $config_file "camera")_$(yq r $config_file "serial_num")
    else
      python3 Camera/images_svo.py --input_svo_file $SCENE --input_config_file $(pwd)/$config_file ;
      yq w -i $config_file "working_path" $dockers_path/$(yq r $config_file "camera")_$(yq r $config_file "serial_num") && \
      docker exec OPENMVG bash ./$dockers_path/$working_code/OpenMVG/camera.sh /$dockers_path/$working_code/$config_file ;
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
    docker exec OPENMVG bash ./$dockers_path/$working_code/OpenMVG/cameras_Known.sh /$dockers_path/$working_code/$config_file ;
    yq w -i $config_file "working_path" $MAIN/$(yq r $config_file "camera")_$(yq r $config_file "serial_num") && \
    echo 'Error study: 1. Plane 3D:' && \
    python3 Error_study/plane3D.py $(pwd)/$config_file && \
    echo 'Error study: 2. Scale Factor:' && \
    python3 Error_study/scale.py $(pwd)/$config_file && \
    echo 'Error study: 3. Scene Rescale:' && \
    python3 Error_study/rescale.py $(pwd)/$config_file && \
    echo 'Error study: 4. Distances error:' && \
    python3 Error_study/measures.py $(pwd)/$config_file && \
    echo 'Error study: 5. Reprojection error:' && \
    python3 Error_study/reprojection.py $(pwd)/$config_file && \
    echo 'Error study: 6. Depth difference:' && \
    python3 Error_study/depth.py $(pwd)/$config_file
  fi
done

echo 'Error parameterisation'
python3 Error_study/sistematic_error.py $(pwd)/$config_file
echo 'Error Regression'
python3 Error_study/ZED_parameterisation_one_by_one.py $(pwd)/$config_file
echo 'Error correction study'
python3 Error_study/correct_depth_each.py $(pwd)/$config_file

yq w -i $config_file "user_id" 0
yq w -i $config_file "user_group" 0

if [ "$ZED_SDK_V" == "v4" ]; then
  docker stop ZED
fi

docker stop OPENMVG