##############################
#  Created on: June 12, 2024 #
#  Author: Adriana GV        #
##############################

# Libraries
import sys
import numpy as np
import json
import yaml
import copy
from tqdm import tqdm

config_f =  sys.argv[1]
with open(config_f, 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Parameters & directories
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
# App paths
plane3D_path = f'{output_path}/{config["plane_path"]}'
calib_path = f'{main_path}/{config["calibration_path"]}'
# App files
struc_file = './jsons_structures.json'
chessboard_scaled_sfm = f'{output_path}/{config["scaled_known_sfm_data"]}'
plane_sfm = f'{plane3D_path}/{config["plane_file"]}'
savefile = f'{calib_path}/{config["extrinsics_file"]}'

# Read Plane JSON
with open(plane_sfm, 'r') as plane:
    plane_info = json.load(plane)
plane.close

# Read sfm_data
with open(chessboard_scaled_sfm, 'r') as recons:
    sfm_data = json.load(recons)
recons.close

# YAML Structure
# Read the reconstruction data
with open(struc_file) as y:
    struct = json.load(y)
y.close

fe = struct["Floor_Extrinsics"]
e = struct["Cam_Extrinsic"]

filenames = []
keys = []
id_poses = []
for view in sfm_data["views"]:
    filename = view["value"]["ptr_wrapper"]["data"]["filename"]
    if filename.startswith('left'):
        filenames.append(filename)
        id_pose = view["value"]["ptr_wrapper"]["data"]["id_pose"]
        id_poses.append(id_pose)
        key = view["value"]["ptr_wrapper"]["data"]["id_view"]
        keys.append(key)

# Find the best point
min_dist = plane_info["Error with respect to the plane"]["Mix. value"]
best_point_key = 0
for point in plane_info["Distance to the plane per point"]:
    if point["Distance"] == min_dist:
        best_point_key = point["Point ID"]
    else:
        continue

point_t = ''
for corner in sfm_data["structure"]:
    if corner["key"] == best_point_key:
        point_t = corner["value"]["X"]


for ext in tqdm(sfm_data["extrinsics"]):

    try:
        match = id_poses.index(ext["key"])
    except:
        right_image = True

    if not right_image:
        ext["value"]["center"] -= point_t
        cam_t = -np.dot(ext["value"]["rotation"],ext["value"]["center"])
        e["Model"] = filename[match].split("_")[1]
        e["SN"] = filename[match].split("_")[2].split(".")[0]
        e["R"] = ext["value"]["rotation"].tolist()
        e["t"] = cam_t

        fe["Left_cams"].append(copy.deepcopy(e))



with open(savefile, 'a') as cam_extrinsic:
    yaml.dump(fe, cam_extrinsic, indent=4)
cam_extrinsic.close