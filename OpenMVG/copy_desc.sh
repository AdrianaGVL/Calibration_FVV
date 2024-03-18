# Script for copy 6144 bytes OpenMVG .desc files

# Paths
DATASET='/media/agv/JesusGTI/Calibration/iPhone_Recordings/D_Chess'
OUTPUT=$DATASET'/output'
# mkdir $OUTPUT
MATCHES=$OUTPUT'/matches'
MYMATCHES=$OUTPUT/matches_for_known

# Loop through files in the target directory
for file in "$MATCHES"/*".desc"; do
  if [ -f "$file" ]; then
  	base_name=$(basename ${file})
	echo $base_name
    { head -c6400 > "$MYMATCHES/$base_name"; } < $file
  fi
done