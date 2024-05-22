#######################
#  Created on: May 22, 2024
#  Author: Adriana GV
#######################

# Libraries
import numpy as np
import json
import yaml
import os
import cv2
import statistics
import matplotlib.pyplot as plt
import seaborn as sns

with open('./config_file.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Parameters & directories
camera = config["camera"]
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
depth_frames = f'{scene}/{config["depth_frames_folder"]}'
output_path = f'{scene}/{config["out_path"]}'
# App paths
savepath = f'{output_path}/{config["depth_path"]}'
os.makedirs(savepath, exist_ok=True)
# App files
reprojection_sfm = f'{savepath}/{config["reprojection_file"]}'
savefile = f'{savepath}/{config["depth_file"]}'

with open(reprojection_sfm, 'r') as recosntruction:
    sfm_data = json.load(recosntruction)
recosntruction.close

f = sfm_data["intrinsics"][0]["value"]["ptr_wrapper"]["data"]["focal_length"]
ppx = sfm_data["intrinsics"][0]["value"]["ptr_wrapper"]["data"]["principal_point"][0]
ppy = sfm_data["intrinsics"][0]["value"]["ptr_wrapper"]["data"]["principal_point"][1]
kmatrix = np.array([[f, 0, ppx],[0, f, ppy],[0, 0, 1]])

filenames = []
keys = []
for view in sfm_data["views"]:
    filename = view["value"]["ptr_wrapper"]["data"]["filename"]
    filenames.append(filename)
    key = view["value"]["ptr_wrapper"]["data"]["id_view"]
    keys.append(key)

depths_error = []
pix_err_x = []
pix_err_y = []
print(f'Running depth study for {len(sfm_data["structure"])} points')
for point in sfm_data["structure"]:
    pos = 0
    for feat in point["value"]["observations"]:
        # Associanted frame
        try:
            match = keys.index(feat["key"])
        except:
            match = 'None'
            
        if type(match) == int:
            name_frame = filenames[match]
            depth_frame = cv2.imread(f'{depth_frames}/{name_frame}')
            # Camera pose
            R = np.array(sfm_data["extrinsics"][match]["value"]["rotation"])
            c = np.array(sfm_data["extrinsics"][match]["value"]["center"])
            # Translation vector and Extrinsic Matrix
            t = -np.dot(R,c)
            # 3D point coordinates
            cloud_point = np.array(point["value"]["X"])
            # Reprojection Equations
            point_3d = np.append(cloud_point, 1)
            point_in_pose = np.dot(R, point_3d) + t
            coord_x = feat["value"]["x"][0]
            coord_y = feat["value"]["x"][1]
            zed_depth = [coord_x,coord_y]
            depth_error = zed_depth - point_in_pose[2]
            depths_error.append(depth_error)
            # Create new variable in the sfm_data file
            point["value"]["observations"][pos]["depth study"] = {
                "OpenMVG depth": point_in_pose[2],
                "ZED depth": zed_depth,
                "difference": depth_error
            }
            pix_err_x.append(point["value"]["observations"][pos]["reprojection"]["error"][0])
            pix_err_y.append(point["value"]["observations"][pos]["reprojection"]["error"][1])
            pos += 1
        else:
            pos += 1
            continue

sfm_data["Depth study statistics"] = {
    "Mean depth error (mm)": statistics.mean(depths_error),
    "Depth error std (mm)": statistics.stdev(depths_error),
    "Max depth error (mm)": max(depths_error),
    "Min depth error (mm)": min(depths_error)
}

print(f'Saving results in {savepath}')
with open(savefile, 'w') as dpth:
    json.dump(sfm_data, dpth, indent=4)
dpth.close

# Plot depth error
sns.histplot(depths_error, kde=True, color='blue')
plt.title('Depth values difference distribution')
plt.xlabel('Value (mm)')
plt.ylabel('Density (nº points)')
plt.savefig(f'{savepath}/depths_diff.png')
plt.close()

# Depth & Reprojection
fig, ax = plt.subplots()
scatter = ax.scatter(pix_err_x, pix_err_y, c=depths_error, cmap='viridis', s=100)
cbar = plt.colorbar(scatter)
cbar.set_label('Depth error')
ax.set_xlabel('Reprojection error in X-axis')
ax.set_ylabel('Reprojection error in Y-axis')
ax.set_title('Depth error compared to the reprojection error')
plt.savefig(f'{savepath}/depth_reproj.png')