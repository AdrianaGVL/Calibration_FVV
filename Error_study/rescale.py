#######################
#  Created on: April 15, 2024
#  Author: Adriana GV
#######################

# Libraries
import json

# Paths
scene = 'Video_Chess_D'
main_path = '/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
scene_path = f'{main_path}/{scene}'
results_path = f'{scene_path}/output'
sfm_data_file = f'{results_path}/Reconstruction_for_known/cloud_and_poses.json'
chess_measures_file = f'{results_path}/measures_chess.json'
rescale_file = f'{results_path}/cloud_and_poses_mm.json'

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