#######################
#  Created on: May 16, 2024
#  Author: Adriana GV
#######################

config_file="./config_file.yml"

yq_v=$(yq --version 2>&1)
if [ "$yq_v" == "yq version 3.4.1" ]; then
    MAIN=$(yq r $config_file "working_path")
    SCENE=$MAIN/$(yq r $config_file "scene")
else
    MAIN=$(yq e '.working_path' "$config_file")
    SCENE=$MAIN/$(yq e '.scene' "$config_file")
fi

python3 ./Camera/images_svo.py --input_svo_file $SCENE