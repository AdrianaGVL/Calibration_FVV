#######################
#  Created on: June 13, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import yaml
import statistics
import copy
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import analysis_tools as aly

# Config file
with open('./config_file.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Paths
camera = config["camera"]
sn = config["serial_num"]
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
depth_frames = f'{scene}/{config["depth_frames_folder"]}'
output_path = f'{scene}/{config["out_path"]}'
dept_params = f'{output_path}/{camera}/{config["depth_correction_file"]}'
# App paths
reconstruction_known = f'{output_path}/{config["known_poses"]}'
results_path = f'{output_path}/{config["scale_data"]}'
os.makedirs(results_path, exist_ok=True)
# App files
jsons_path = './jsons_structures.json'
sfm_data_file = f'{reconstruction_known}/{config["known_sfm_data"]}'
scales_data = f'{results_path}/{config["scales_file"]}'

# JSON Structure
with open(jsons_path) as j:
    json_model = json.load(j)
j.close

scale = json_model["Scales"]

# Read the reconstruction data
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

# Read depth correction
with open(f'{dept_params}', 'r') as params:
    depth_params = yaml.safe_load(params)
params.close

if depth_params["Camera"]["Serial number"] == f'{sn}':
    a = depth_params["Camera"]["a"]
    b = depth_params["Camera"]["b"]
    offset = depth_params["Camera"]["offset"]
else:
    print("The camera hasn't been parameterised")
    exit

filenames = []
keys = []
for view in sfm_data["views"]:
    filename = view["value"]["ptr_wrapper"]["data"]["filename"]
    filenames.append(filename)
    key = view["value"]["ptr_wrapper"]["data"]["id_view"]
    keys.append(key)

nan_value = 0
camera_depth, mvg_depth = [], []
for point in tqdm(sfm_data["structure"]):
    for feat in tqdm(point["value"]["observations"]):
        # Associanted frame
        try:
            match = keys.index(feat["key"])
        except:
            match = 'None'
            
        if type(match) == int:
            # Camera pose
            for pose in sfm_data["extrinsics"]:
                if feat["key"] == pose["key"]:
                    R = np.array(pose["value"]["rotation"])
                    c = np.array(pose["value"]["center"])
                else:
                    continue
            # Load depth map
            name_frame = filenames[match]
            num_format = name_frame.split('_')
            only_num = num_format[1].split('.')
            depth_frame_name = f'depth_{only_num[0]}.npy'
            depthmap = np.load(f'{depth_frames}/{depth_frame_name}')
            # Is camera value valid?
            coord_x = round(feat["value"]["x"][0])
            coord_y = round(feat["value"]["x"][1])
            zed_depth = depthmap.T[coord_x, coord_y]
            if math.isnan(zed_depth) or math.isinf(zed_depth) or zed_depth == 0.0:
                nan_value += 1
            else:
                # Translation vector and Extrinsic Matrix
                # 3D point coordinates
                cloud_point = np.array(point["value"]["X"])
                translated_point = cloud_point - c
                # Reprojection Equations
                point_in_pose = np.dot(R, translated_point)
                mvg_dvalue = point_in_pose[2]
                camera_depth.append(zed_depth)
                mvg_depth.append(mvg_dvalue)
            pos += 1
        else:
            pos += 1
            continue

# Depth correction
corrected_depth = []
for value in camera_depth:
    good_depth = ((a*(value**2)) + (b*value) + offset)
    corrected_depth.append(good_depth)

scales = []
for i in range(len(corrected_depth)):
    scale = corrected_depth[i]/mvg_depth[i]
    scales.append(scale)

# Save data
scale["Scaling Factor"]["Mean"] = aly.mae_study(scales)[0]
scale["Scaling Factor"]["Standard deviation"] = aly.mae_study(scales)[1]
scale["Scaling Factor"]["Max. value"] = max(scales)
scale["Scaling Factor"]["Min. value"] = min(scales)

with open(scales_data, 'w') as pqs:
    json.dump(scale, pqs, indent=4)
pqs.close