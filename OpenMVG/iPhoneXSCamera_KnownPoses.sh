#######################
#  Created on: March 18, 2024
#  Author: Adriana GV
#######################

# Script for iPhone XS Max Images (iPhone XS Max camera)

# Paths
MAIN='/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
SCENE=$MAIN'/Video_Chess_C'
OUTPUT=$SCENE'/output_chiquito'
MATCHES=$OUTPUT'/matches_for_known'
RECONSTRUCTION=$OUTPUT'/Reconstruction_for_known'
mkdir -p $RECONSTRUCTION
# MVS=$OUTPUT'/mvs'
# mkdir -p $MVS
# UNDISTOR=$OUTPUT/Undistorted
# mkdir -p $UNDISTOR

 # Error search paths
 # SVG_MATCHING=$OUTPUT'/svg_corners'
# mkdir -p $SVG_MATCHING
# TRACKS=$OUTPUT'/tracks'
# mkdir -p $TRACKS


# # OpenMVG Execution
# # Test to see if matches and tracks are correct before executing the reconstruction
# # View Matches
# echo 'Executing Export (to SVG format) Matches'
# openMVG_main_exportMatches -i $OUTPUT/sfm_data.json -d $MATCHES -m $MATCHES/matches.putative.txt -o $SVG_MATCHING
# #View Tracks
# echo 'Executing Export (to SVG format) Tracks'
# openMVG_main_exportMatches -i $OUTPUT/sfm_data.json -d $MATCHES -m $MATCHES/matches.putative.txt -o $TRACKS

# Final Results
# 1. Compute Structure from Motion
echo '1. Executing Strucuture from Motion'
openMVG_main_ComputeStructureFromKnownPoses -i $OUTPUT/sfm_data.json -m $MATCHES -o $RECONSTRUCTION/cloud_and_poses.bin -d -f $MATCHES/matches.f.txt
# openMVG_main_SfM -i $OUTPUT/sfm_data.json -m $MATCHES -o $RECONSTRUCTION -s INCREMENTALV2 -S EXISTING_POSE -M $MATCHES/matches.f.txt

# 2. New SfM data conversion to JSON
echo '2. Executing SfM data conversion to JSON'
openMVG_main_ConvertSfM_DataFormat -i $RECONSTRUCTION/cloud_and_poses.bin -o $RECONSTRUCTION/cloud_and_poses.json

# 3. Colorise the reconstruction
echo '3. Executing Colouring Reconstruction'
openMVG_main_ComputeSfM_DataColor -i $RECONSTRUCTION/cloud_and_poses.json -o $RECONSTRUCTION/cloud_and_poses_colour.ply

## 4. MeshLab conversion
echo '4. Executing MeshLab conversion'
openMVG_main_openMVG2MESHLAB -i $RECONSTRUCTION/cloud_and_poses.json -p $RECONSTRUCTION/cloud_and_poses_colour.ply -o $RECONSTRUCTION

## Extra - 1. MVS conversion (files are the same but instead of points, triangles)
#echo ' Extra - 1. Executing MVS conversion'
#openMVG_main_openMVG2openMVS -i $RECONSTRUCTION/cloud_and_poses.bin -o $MVS/cloud_and_poses.mvs -d $UNDISTOR

# Options per command
# 1. Compute Structure From Known Poses
	# [-i|--input_file] path to a SfM_Data scene
	# [-m|--match_dir] path to the features and descriptors that corresponds to the provided SfM_Data scene
	# [-o|--output_file] file where the output data will be stored (i.e. path/sfm_data_structure.bin)

	# [Triangulation mode]:
	# [A. No Provided Matches -> Triangulation of guided epipolar geometry matches (default mode)]
	# 	[-p|--pair_file] path to a pairs file (only those pairs will be considered to compute the structure)
	# 	[-f|--match_file] path to a matches file (loaded pair indexes will be used)
	# [B. Provided Matches -> Robust triangulation of the match file (activated by -d)]
	# 	[-d|--direct_triangulation] Robustly triangulate the tracks computed from the file given by [-f|--match_file]
	# 	[-f|--match_file] path to a matches file (loaded pair indexes will be used)
	# [C. Tracks stored as landmark observations in a sfm_data file]
	# 	[-T|--sfm_data_tracks] path to sfm_data files with Landmarks observations (i.e from openMVG_main_VO)
	# [-t|--triangulation_method] triangulation method (default=3):
	# 	0: DIRECT_LINEAR_TRANSFORM
	# 	1: L1_ANGULAR
	# 	2: LINFINITY_ANGULAR
	# 	3: INVERSE_DEPTH_WEIGHTED_MIDPOINT

	# [Optional]
	# [-b|--bundle_adjustment] (switch) perform a bundle adjustment on the scene (OFF by default)
	# [-r|--residual_threshold] maximal pixels reprojection error that will be considered for triangulations (4.0 by default)
	# [-c|--cache_size]
	# Use a regions cache (only cache_size regions will be stored in memory)
	# If not used, all regions will be load in memory.

