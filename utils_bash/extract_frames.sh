#######################
#  Created on: May 16, 2024
#  Author: Adriana GV
#######################


# Script for SVO2 Repearing files
# Run in docker: ./dataset/extract_frames.sh

MAIN=$(yq e '.working_path' "$config_file")

for SCENE in "$MAIN"/*/; do
    for VIDEO in $SCENE/*_repaired.svo2; do
        python3 ZED/images_svo.py --input_svo_file $VIDEO --output_path $SCENE
    done
done

# python3 ZED/images_svo.py  --input_svo_file dataset/Sala_jesus/HD1080_SN27926127_13-26-08_repaired.svo2 --output_path dataset/Sala_jesus/svo_images && \
# python3 ZED/images_svo.py  --input_svo_file dataset/sala_yo/HD1080_SN27926127_12-00-02_repaired.svo2 --output_path dataset/sala_yo/svo_images && \
# python3 ZED/images_svo.py  --input_svo_file dataset/sala_cameras/HD1080_SN27926127_11-32-56_repaired.svo2 --output_path dataset/sala_cameras/svo_images
# python3 ZED/images_svo.py  --input_svo_file dataset/sala_sillon/HD1080_SN27926127_13-11-47_repaired.svo2 --output_path dataset/sala_sillon/svo_images && \