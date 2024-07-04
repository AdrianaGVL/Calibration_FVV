#!/bin/bash

#######################
#  Created on: June 13, 2024
#  Author: Adriana GV
#######################

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

# Paths
# config_file="/dataset/config_file.yml"
config_file=$1

USER_ID=$(yq e '.user_id' "$config_file")
GROUP_ID=$(yq e '.user_group' "$config_file")

MAIN=$(yq e '.working_path' "$config_file")
SCENE=$MAIN/$(yq e '.scene' "$config_file")
OUTPUT=$SCENE/$(yq e '.out_path' "$config_file")
MYMATCHES=$OUTPUT'/matches_for_known'
RECONSTRUCTION=$OUTPUT/$(yq e '.known_poses' "$config_file")
mkdir -p $RECONSTRUCTION

# 1. Compute Structure from Motion
echo '1. Executing Strucuture from Motion'
openMVG_main_ComputeStructureFromKnownPoses -i $OUTPUT/sfm_data.json -m $MYMATCHES -o $RECONSTRUCTION/cloud_and_poses.bin -d -f $MYMATCHES/matches.f.txt

# 2. New SfM data conversion to JSON
echo '2. Executing SfM data conversion to JSON'
openMVG_main_ConvertSfM_DataFormat -i $RECONSTRUCTION/cloud_and_poses.bin -o $RECONSTRUCTION/cloud_and_poses.json

chown -R $USER_ID:$GROUP_ID $OUTPUT
chown -R $USER_ID:$GROUP_ID $MATCHES
chown -R $USER_ID:$GROUP_ID $RECONSTRUCTION

# Options per command
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
