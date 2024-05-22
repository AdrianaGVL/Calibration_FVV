#######################
#  Created on: April 15, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import yaml

# Config file
with open('./config_file.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Paths
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
sfm_data_file = f'{output_path}/{config["sfm_data"]}'
scale_info = f'{output_path}/{config["scale_data"]}'
rescale_file = f'{output_path}/{config["sfm_data_scaled"]}'
chess_measures_file = f'{scale_info}/{config["measures_file"]}'

# Read the reconstruction data
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

# Read the scale info
with open(chess_measures_file) as f:
    scales = json.load(f)
f.close

# Obtain the mean scale
scale = scales["Measures"]["Scaling Factor"]["Mean"]

# Rescale camera pose
poses = range(len(sfm_data["extrinsics"]))
for pose in poses:
    axes = range(len(sfm_data["extrinsics"][pose]["value"]["rotation"]))
    coords = range(len(sfm_data["extrinsics"][pose]["value"]["center"]))
    for axis in axes:
        values = range(len(sfm_data["extrinsics"][pose]["value"]["rotation"][axis]))
        for value in values:
            sfm_data["extrinsics"][pose]["value"]["rotation"][axis][value] *= scale
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