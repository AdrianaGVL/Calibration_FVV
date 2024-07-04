#######################
#  Created on: April 15, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import yaml
import sys

# Config file
config_f =  sys.argv[1]
with open(config_f, 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Paths
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
# App directory
scale_info = f'{output_path}/{config["scale_data"]}'
# App files
chess_measures_file = f'{scale_info}/{config["scales_file"]}'
sfm_data_file = f'{output_path}/{config["sfm_data"]}'
rescale_file = f'{output_path}/{config["sfm_data_scaled"]}'
checker_sfm_data_file = f'{output_path}/{config["known_poses"]}/{config["known_sfm_data"]}'
checker_scaled = f'{output_path}/{config["scaled_known_sfm_data"]}'

# Read the reconstruction data
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

# Read the scale info
with open(chess_measures_file) as f:
    scales = json.load(f)
f.close

# Obtain the mean scale
scale = scales["Scaling Factor"]["Mean"]

# Rescale camera center
poses = range(len(sfm_data["extrinsics"]))
for pose in poses:
    coords = range(len(sfm_data["extrinsics"][pose]["value"]["center"]))
    for coord in coords:
        sfm_data["extrinsics"][pose]["value"]["center"][coord] *= scale

# Rescale the points coordinates
points = range(len(sfm_data["structure"]))
for point in points:
    coordinates = range(len(sfm_data["structure"][point]["value"]["X"]))
    for coordinate in coordinates:
        sfm_data["structure"][point]["value"]["X"][coordinate] *= scale

with open(rescale_file, 'w') as rs:
    json.dump(sfm_data, rs, indent=4)
rs.close

# Read the reconstruction data
with open(checker_sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

# Rescale camera center
poses = range(len(sfm_data["extrinsics"]))
for pose in poses:
    coords = range(len(sfm_data["extrinsics"][pose]["value"]["center"]))
    for coord in coords:
        scaled_pose = float(scale)*float(sfm_data["extrinsics"][pose]["value"]["center"][coord])
        sfm_data["extrinsics"][pose]["value"]["center"][coord] = float(scaled_pose)

# Rescale the points coordinates
points = range(len(sfm_data["structure"]))
for point in points:
    coordinates = range(len(sfm_data["structure"][point]["value"]["X"]))
    for coordinate in coordinates:
        scaled_point = float(scale)*float(sfm_data["structure"][point]["value"]["X"][coordinate])
        sfm_data["structure"][point]["value"]["X"][coordinate] = float(scaled_point)

with open(checker_scaled, 'w') as rs:
    json.dump(sfm_data, rs, indent=4)
rs.close