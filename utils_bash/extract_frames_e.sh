#######################
#  Created on: May 16, 2024
#  Author: Adriana GV
#######################

# Config file path
config_file=$1

yq_v=$(yq --version 2>&1)
if [ "$yq_v" == "yq version 3.4.1" ]; then
    MAIN=$(yq r $config_file "working_path")
    SCENE=$MAIN/$(yq r $config_file "scene")
else
    MAIN=$(yq e '.working_path' "$config_file")
    SCENE=$MAIN/$(yq e '.scene' "$config_file")
fi

for VIDEO in $SCENE/*.{svo2,svo}; do
    if [ -f "$VIDEO" ]; then
        python3 ./Camera/images_svo_e.py --input_svo_file $VIDEO --output_path $SCENE
        # rm $VIDEO
    fi
done