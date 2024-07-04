#######################
#  Created on: June 12, 2024
#  Author: Adriana GV
#######################

# Libraries
import os
import yaml
import json
import utils_dim as udim

# Config file
with open('./config_DL.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Paths
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
frames_path = f'{scene}/{config["frames_folder"]}'
sfm_data = f'{output_path}/{config["init_sfm_data"]}'
dim_features = f'{scene}/{config["dim_results_path"]}/features.h5'
dim_matches = f'{scene}/{config["dim_results_path"]}/matches.h5'
savepath = f'{output_path}/matches_dim'
# os.makedirs(savepath, exist_ok=True)

# ID given by OpenMVG
with open(sfm_data) as f:
    sfm_data = json.load(f)
f.close

# OpenMVG nomeclature
filenames = []
ids = []
for view in sfm_data["views"]:
    filename = view["value"]["ptr_wrapper"]["data"]["filename"]
    filenames.append(filename)
    id = view["value"]["ptr_wrapper"]["data"]["id_view"]
    ids.append(id)

# Features.h5 to .feat & .desc
udim.add_keypoints(dim_features, frames_path, savepath)
# Matches.h5 to matches.putative.bin, matches.f.bin & pairs
# udim.add_matches(dim_matches, savepath, filenames, ids)