#######################
#  Created on: May 16, 2024
#  Author: Adriana GV
#######################


# Script for SVO2 Repearing files
# Run in docker: ./dataset/repair.sh

MAIN=$(yq e '.working_path' "$config_file")

for SCENE in "$MAIN"/*/; do
    for VIDEO in $SCENE/*.svo2; do
        ./usr/local/zed/tools/ZED_SVO_Editor -repair $VIDEO
    done
done

# ./usr/local/zed/tools/ZED_SVO_Editor -repair dataset/Sala_dani/HD1080_SN27926127_13-34-08.svo2 \
# ./usr/local/zed/tools/ZED_SVO_Editor -repair dataset/Sala_jesus/HD1080_SN27926127_13-26-08.svo2 \
# ./usr/local/zed/tools/ZED_SVO_Editor -repair dataset/sala_sillon/HD1080_SN27926127_13-11-47.svo2 \
# ./usr/local/zed/tools/ZED_SVO_Editor -repair dataset/sala_yo/HD1080_SN27926127_12-00-02.svo2