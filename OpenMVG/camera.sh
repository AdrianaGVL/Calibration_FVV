#!/bin/bash

#######################
#  Created on: March 18, 2024
#  Author: Adriana GV
#######################

# Script for camera

# Libraries
# YAML
if ! command -v yq &>/dev/null; then
  echo "Error: 'yq' command not found. Please install yq"
  echo "Linux example: sudo apt-get install yq"
  echo "macOS example: brew install yq"
  exit 1
fi
# JSON
if ! command -v jq &>/dev/null; then
  echo "Error: 'jq' command not found. Please install jq"
  echo "Linux example: sudo apt-get install jq"
  echo "macOS example: brew install jq"
  exit 1
fi

# Config file
config_file=$1

USER_ID=$(yq e '.user_id' "$config_file")
GROUP_ID=$(yq e '.user_group' "$config_file")

# Paths
MAIN=$(yq e '.working_path' "$config_file")
SCENE=$MAIN/$(yq e '.scene' "$config_file")
DATASET=$SCENE/$(yq e '.frames_folder' "$config_file")
OUTPUT=$SCENE/$(yq e '.out_path' "$config_file")
mkdir -p $OUTPUT
MATCHES=$OUTPUT'/matches'
mkdir -p $MATCHES
RECONSTRUCTION=$OUTPUT/Reconstruction
mkdir -p $RECONSTRUCTION

# Initial intrinsic matrix (pixels)
calibration_file=$SCENE/$(yq e '.calibration' "$config_file")
fx=$(jq -r '.intrinsic[0]["focal length left camera"][0]' "$calibration_file")
fy=$(jq -r '.intrinsic[0]["focal length left camera"][1]' "$calibration_file")
cx=$(jq -r '.intrinsic[0]["principal_point"][0]' "$calibration_file")
cy=$(jq -r '.intrinsic[0]["principal_point"][1]' "$calibration_file")
K="$fx;0;$cx;0;$fy;$cy;0;0;1"

# openMVG Execution
# 1. Images Listing
echo '1. Executing Images Listing'
openMVG_main_SfMInit_ImageListing -i $DATASET -k $K -o $OUTPUT -c 1 -g 1

mv $OUTPUT/sfm_data.json $OUTPUT/sfm_data_no_poses.json

#2. Features Computation
echo '2. Executing Features Computation'
openMVG_main_ComputeFeatures -i $OUTPUT/sfm_data_no_poses.json -o $MATCHES -m SIFT -p ULTRA -n 8

# 3. Pair Generator
echo '3. Executing Pair Generator'
openMVG_main_PairGenerator -i $OUTPUT/sfm_data_no_poses.json -o $MATCHES/pairs.bin -m EXHAUSTIVE

# 4. Matches Computation
echo '4. Executing Matches Computation'
openMVG_main_ComputeMatches -i $OUTPUT/sfm_data_no_poses.json -o $MATCHES/matches.putative.bin -p $MATCHES/pairs.bin -n AUTO

# 5. Geometric Filtering
echo '5. Executing Geometric Filtering'
openMVG_main_GeometricFilter -i $OUTPUT/sfm_data_no_poses.json -m $MATCHES/matches.putative.bin -o $MATCHES/matches.f.bin -p $MATCHES/pairs.bin

# 6. Compute Structure from Motion
echo '6. Executing Strucuture from Motion'
openMVG_main_SfM -i $OUTPUT/sfm_data_no_poses.json -m $MATCHES -o $RECONSTRUCTION -s GLOBAL -f NONE -M $MATCHES/matches.f.bin

# 7. New SfM data conversion to JSON
echo '7. Executing SfM data conversion to JSON'
openMVG_main_ConvertSfM_DataFormat -i $RECONSTRUCTION/sfm_data.bin -o $RECONSTRUCTION/sfm_data.json

mv $RECONSTRUCTION/sfm_data.json $OUTPUT/sfm_data.json

# 8. Colorise Reconstrucion
echo '8. Executing Colouring Reconstruction'
openMVG_main_ComputeSfM_DataColor -i $OUTPUT/sfm_data.json -o $RECONSTRUCTION/cloud_and_poses_colour.ply

# 9. MeshLab conversion
echo '9. Executing MeshLab Conversion'
openMVG_main_openMVG2MESHLAB -i $OUTPUT/sfm_data.json -p $RECONSTRUCTION/cloud_and_poses_colour.ply -o $RECONSTRUCTION

chown -R $USER_ID:$GROUP_ID $OUTPUT
chown -R $USER_ID:$GROUP_ID $MATCHES
chown -R $USER_ID:$GROUP_ID $RECONSTRUCTION

# Options per command
# 1. Image Listing Options
	#[-i|--imageDirectory]
	#[-d|--sensorWidthDatabase]
	#[-o|--outputDirectory]
	#[-f|--focal] (pixels)
	#[-k|--intrinsics] Kmatrix: "f;0;ppx;0;f;ppy;0;0;1"
	#[-c|--camera_model] Camera model type:
	#	1: Pinhole
	#	2: Pinhole radial 1
	#	3: Pinhole radial 3 (default)
	#	4: Pinhole brown 2
	#	5: Pinhole with a simple Fish-eye distortion
	#	7: Spherical camera
	#[-g|--group_camera_model]
	#	 0-> each view have it's own camera intrinsic parameters,
	#	 1-> (default) view can share some camera intrinsic parameters

	#[-P|--use_pose_prior] Use pose prior if GPS EXIF pose is available[-W|--prior_weights] "x;y;z;" of weights for each dimension of the prior (default: 1.0)
	#[-m|--gps_to_xyz_method] XZY Coordinate system:
	#	 0: ECEF (default)
	#	 1: UTM

# 2. Features Computation
	#[-i|--input_file] a SfM_Data file
	#[-o|--outdir path]

	#[Optional]
	#[-f|--force] Force to recompute data
	#[-m|--describerMethod]
	#  (method to use to describe an image):
	#   SIFT (default),
	#   SIFT_ANATOMY,
	#   AKAZE_FLOAT: AKAZE with floating point descriptors,
	#   AKAZE_MLDB:  AKAZE with binary descriptors
	#[-u|--upright] Use Upright feature 0 or 1
	#[-p|--describerPreset]
	#  (used to control the Image_describer configuration):
	#   NORMAL (default),
	#   HIGH,
	#   ULTRA: !!Can take long time!!
	#[-n|--numThreads] number of parallel computations

# 3. Pair Generator
	#[-i|--input_file]         A SfM_Data file
	#[-o|--output_file]        Output file where pairs are stored

	#[Optional]
	#[-m|--pair_mode] mode     Pair generation mode
	#       EXHAUSTIVE:        Build all possible pairs. [default]
	#       CONTIGUOUS:        Build pairs for contiguous images (use it with --contiguous_count parameter)
	#[-c|--contiguous_count] X Number of contiguous links
	#       X: will match 0 with (1->X), ...]
	#       2: will match 0 with (1,2), 1 with (2,3), ...
	#       3: will match 0 with (1,2,3), 1 with (2,3,4), ...

# 4. Matches Computation
	#[-i|--input_file]   A SfM_Data file
	#[-o|--output_file]  Output file where computed matches are stored
	#[-p|--pair_list]    Pairs list file

	#[Optional]
	#[-f|--force] Force to recompute data]
	#[-r|--ratio] Distance ratio to discard non meaningful matches
	#   0.8: (default).
	#[-n|--nearest_matching_method]
	#  AUTO: auto choice from regions type,
	#  For Scalar based regions descriptor:
	#    BRUTEFORCEL2: L2 BruteForce matching,
	#    HNSWL2: L2 Approximate Matching with Hierarchical Navigable Small World graphs,
	#    HNSWL1: L1 Approximate Matching with Hierarchical Navigable Small World graphs
	#      tailored for quantized and histogram based descriptors (e.g uint8 RootSIFT)
	#    ANNL2: L2 Approximate Nearest Neighbor matching,
	#    CASCADEHASHINGL2: L2 Cascade Hashing matching.
	#    FASTCASCADEHASHINGL2: (default)
	#      L2 Cascade Hashing with precomputed hashed regions
	#     (faster than CASCADEHASHINGL2 but use more memory).
	#  For Binary based descriptor:
	#    BRUTEFORCEHAMMING: BruteForce Hamming matching,
	#    HNSWHAMMING: Hamming Approximate Matching with Hierarchical Navigable Small World graphs
	#[-c|--cache_size]
	#  Use a regions cache (only cache_size regions will be stored in memory)
	#  If not used, all regions will be load in memory.
	#[Pre-emptive matching:]
	#[-P|--preemptive_feature_count] <NUMBER> Number of feature used for pre-emptive matching

# 5. Geometric Filtering
	#[-i|--input_file]       A SfM_Data file
	#[-m|--matches]          (Input) matches filename
	#[-o|--output_file]      (Output) filtered matches filename

	#[Optional]
	#[-p|--input_pairs]      (Input) pairs filename
	#[-s|--output_pairs]     (Output) filtered pairs filename
	#[-f|--force]            Force to recompute data
	#[-g|--geometric_model]
	#  (pairwise correspondences filtering thanks to robust model estimation):
	#   f: (default) fundamental matrix,
	#   e: essential matrix,
	#   h: homography matrix.
	#   a: essential matrix with an angular parametrization,
	#   u: upright essential matrix with an angular parametrization,
	#   o: orthographic essential matrix.
	#[-r|--guided_matching]  Use the found model to improve the pairwise correspondences.
	#[-c|--cache_size]
	#  Use a regions cache (only cache_size regions will be stored in memory)
	#  If not used, all regions will be load in memory.

# 6. Structure from Motion
	#[Required]
	#[-i|--input_file] path to a SfM_Data scene
	#[-m|--match_dir] path to the matches that corresponds to the provided SfM_Data scene
	#[-o|--output_dir] path where the output data will be stored
	#[-s|--sfm_engine] Type of SfM Engine to use for the reconstruction
	#	 INCREMENTAL   : add image sequentially to a 2 view seed
	#	 INCREMENTALV2 : add image sequentially to a 2 or N view seed (experimental)
	#	 GLOBAL        : initialize globally rotation and translations
	#	 STELLAR       : n-uplets local motion refinements + global SfM

	#[Optional parameters]
	#[Common]
	#[-M|--match_file] path to the match file to use (i.e matches.f.txt or matches.f.bin)
	#[-f|--refine_intrinsic_config] Intrinsic parameters refinement option
	#	 ADJUST_ALL -> refine all existing parameters (default)
	#	 NONE -> intrinsic parameters are held as constant
	#	 ADJUST_FOCAL_LENGTH -> refine only the focal length
	#	 ADJUST_PRINCIPAL_POINT -> refine only the principal point position
	#	 ADJUST_DISTORTION -> refine only the distortion coefficient(s) (if any)
	#	 -> NOTE: options can be combined thanks to '|'
	#	 ADJUST_FOCAL_LENGTH|ADJUST_PRINCIPAL_POINT
	#		-> refine the focal length & the principal point position
	#	 ADJUST_FOCAL_LENGTH|ADJUST_DISTORTION
	#		-> refine the focal length & the distortion coefficient(s) (if any)
	#	 ADJUST_PRINCIPAL_POINT|ADJUST_DISTORTION
	#		-> refine the principal point position & the distortion coefficient(s) (if any)
	#[-e|--refine_extrinsic_config] Extrinsic parameters refinement option
	#	 ADJUST_ALL -> refine all existing parameters (default)
	#	 NONE -> extrinsic parameters are held as constant
	#[-P|--prior_usage] Enable usage of motion priors (i.e GPS positions) (default: false)
	#[Engine specifics]
	#[INCREMENTAL]
	#	[-a|--initial_pair_a] filename of the first image (without path)
	#	[-b|--initial_pair_b] filename of the second image (without path)
	#	[-c|--camera_model] Camera model type for view with unknown intrinsic:
	#		 1: Pinhole
	#		 2: Pinhole radial 1
	#		 3: Pinhole radial 3 (default)
	#		 4: Pinhole radial 3 + tangential 2
	#		 5: Pinhole fisheye
	#	[--triangulation_method] triangulation method (default=3):
	#		0: DIRECT_LINEAR_TRANSFORM
	#		1: L1_ANGULAR
	#		2: LINFINITY_ANGULAR
	#		3: INVERSE_DEPTH_WEIGHTED_MIDPOINT
	#	[--resection_method] resection/pose estimation method (default=3):
	#		0: DIRECT_LINEAR_TRANSFORM 6Points | does not use intrinsic data
	#		1: P3P_KE_CVPR17
	#		2: P3P_KNEIP_CVPR11
	#		3: P3P_NORDBERG_ECCV18
	#		4: UP2P_KUKELOVA_ACCV10 | 2Points | upright camera
	#[INCREMENTALV2]
	#	[-S|--sfm_initializer] Choose the SfM initializer method:
	#		 'EXISTING_POSE'-> Initialize the reconstruction from the existing sfm_data camera poses
	#		 'MAX_PAIR'-> Initialize the reconstruction from the pair that has the most of matches
	#		 'AUTO_PAIR'-> Initialize the reconstruction with a pair selected automatically
	#		 'STELLAR'-> Initialize the reconstruction with a 'stellar' reconstruction
	#	[-c|--camera_model] Camera model type for view with unknown intrinsic:
	#		 1: Pinhole
	#		 2: Pinhole radial 1
	#		 3: Pinhole radial 3 (default)
	#		 4: Pinhole radial 3 + tangential 2
	#		 5: Pinhole fisheye
	#	[--triangulation_method] triangulation method (default=3):
	#		0: DIRECT_LINEAR_TRANSFORM
	#		1: L1_ANGULAR
	#		2: LINFINITY_ANGULAR
	#		3: INVERSE_DEPTH_WEIGHTED_MIDPOINT
	#	[--resection_method] resection/pose estimation method (default=3):
	#		0: DIRECT_LINEAR_TRANSFORM 6Points | does not use intrinsic data
	#		1: P3P_KE_CVPR17
	#		2: P3P_KNEIP_CVPR11
	#		3: P3P_NORDBERG_ECCV18
	#		4: UP2P_KUKELOVA_ACCV10 | 2Points | upright camera
	#[GLOBAL]
	#	[-R|--rotationAveraging]
	#		 1 -> L1 minimization
	#		 2 -> L2 minimization (default)
	#	[-T|--translationAveraging]:
	#		 1 -> L1 minimization
	#		 2 -> L2 minimization of sum of squared Chordal distances
	#		 3 -> SoftL1 minimization (default)
	#		 4 -> LiGT: Linear Global Translation constraints from rotation and matches
	#[STELLAR]
	#	[-G|--graph_simplification]
	#		 -> NONE
	#		 -> MST_X
	#		 -> STAR_X
	#	[-g|--graph_simplification_value]
	#		 -> Number (default: 5)
