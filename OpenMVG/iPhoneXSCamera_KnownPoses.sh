# Initialise openMVG Docker with the corresponding dataset
# sudo docker run -it --rm --volume /media/agv/JesusGTI/Calibration/:/dataset  openmvg

# Script for Spherical Images (360 camera)

# Paths
# You can choose between 360_Flat or 360_school
DATASET='dataset/iPhone_Recordings/C_chess/frames'
OUTPUT=$DATASET'/output'
mkdir $OUTPUT
MATCHES=$OUTPUT'/matches_for_known'
mkdir $MATCHES
SVG_MATCHING=$OUTPUT'/svg_corners'
mkdir $SVG_MATCHING
TRACKS=$OUTPUT'/tracks'
mkdir $TRACKS
RECONSTRUCTION=$OUTPUT'/Reconstruction_for_known'
mkdir $RECONSTRUCTION
MVS=$OUTPUT'/mvs'
# mkdir $MVS
UNDISTOR=$OUTPUT/Undistorted
# mkdir $UNDISTOR

# Initial Focal Length (in pixels)
INIT_F=4608

# # openMVG Execution
# #1. Export Matches
# echo '\n 1. Exporting Matches, creation of SVG files'
# openMVG_main_exportMatches -i $OUTPUT/sfm_data_with_info.json -d $MATCHES -m $MATCHES/matches.f.txt -o $SVG_MATCHING

# #2. Export Tracks
# echo '\n 2. Exporting Tracks'
# openMVG_main_exportTracks -i $OUTPUT/sfm_data_with_info.json -d $MATCHES -m $MATCHES/matches.f.txt -o $TRACKS

# 3. Compute Structure from Motion
echo '\n 3. Executing Strucuture from Motion \n'
openMVG_main_ComputeStructureFromKnownPoses -i $OUTPUT/sfm_data_with_info.json -m $MATCHES -o $RECONSTRUCTION/sfm_data_structure.bin -p $MATCHES/pairs.txt -f $MATCHES/matches.f.txt

# 4. New SfM data conversion to JSON
echo '\n 4. Executing SfM data conversion to JSON \n'
openMVG_main_ConvertSfM_DataFormat -i $RECONSTRUCTION/sfm_data_structure.bin -o $RECONSTRUCTION/sfm_data_structure.json

# Extra - The MVS files are the same but instead of points, triangles

# 8. MVS conversion
#echo '\n 8. Executing MVS conversion \n'
#openMVG_main_openMVG2openMVS -i $RECONSTRUCTION/sfm_data.bin -o $MVS/scene.mvs -d $UNDISTOR

#

# Options per command
# 1. Export Matches
	# [-i|--input_file file] path to a SfM_Data scene
	# [-d|--matchdir path]
	# [-m|--sMatchFile filename]
	# [-o|--outdir path]
# 2. Export Tracks
	# [-i|--input_file file] path to a SfM_Data scene
	# [-d|--matchdir path]
	# [-m|--sMatchFile filename]
	# [-o|--outdir path]
# 3. Compute Structure From Known Poses
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

