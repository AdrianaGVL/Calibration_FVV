# Script to extract frames from a video

# Paths
MAIN='/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
SCENE=$MAIN'/Video_Chess_D'
OUTPUT=$SCENE'/frames'
mkdir -p $OUTPUT

# Extract only keyframes (I)
# ffmpeg -r 29.97 -i $SCENE/*.MOV -an -c:v copy -q:v 1 -r 29.97 $SCENE/chess.h265
ffmpeg -i $SCENE/*.MOV -vf "select='eq(pict_type,I)'" -vsync vfr $OUTPUT/frame_%02d.png
# ffmpeg -skip_frame nokey -i $SCENE/*.MOV -vsync 0 -frame_pts true $OUTPUT/%02d.png