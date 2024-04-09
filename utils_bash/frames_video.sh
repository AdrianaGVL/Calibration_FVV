#######################
#  Script to extract frames from a video
#  Created on: March 18, 2024
#  Author: Adriana GV
#######################

# Paths
MAIN='/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
SCENE=$MAIN'/Video_Chess_C'
OUTPUT=$SCENE'/frames'
mkdir -p $OUTPUT

# Extract only keyframes (I)
ffmpeg -i $SCENE/*.MOV -vf "select='eq(pict_type,I)'" -vsync vfr $OUTPUT/frame_%02d.png
# ffmpeg -i $SCENE/*.MOV -vf "select='eq(pict_type,I)'" $OUTPUT/frame_%02d.png