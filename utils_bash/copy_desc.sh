#######################
#  Script for copy 6144 bytes OpenMVG .desc files
#  Created on: March 18, 2024
#  Author: Adriana GV
#######################

# Paths
MAIN='/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
SCENE=$MAIN'/Video_Chess_C'
OUTPUT=$SCENE'/output_chiquito'
MATCHES=$OUTPUT'/matches'
MYMATCHES=$OUTPUT/matches_for_known

# Bytes needed
# NUM_CORNERS=1
# LENGTH_UINT=128
# NUM_B=$NUM_CORNERS*$LENGTH_UINT

# Loop through files in the target directory
for file in "$MATCHES"/*".desc"; do
  if [ -f "$file" ]; then
  	base_name=$(basename ${file})
	echo $base_name
    { head -c6144 > "$MYMATCHES/$base_name"; } < $file
  fi
done