#######################
#  Created on: May 17, 2024
#  Author: Adriana GV
#######################

# This can be done manually; P = K[R|-RC] where -RC = t
# But OpenCV has already a function to calclate this
# What will be manually computeated is the error.

# Libraries
import numpy as np
import json
import yaml
import os
import statistics
import matplotlib.pyplot as plt
import seaborn as sns

with open('./config_file.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Path and files
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["path"]}'
sfm_path = f'{output_path}/{config["sfm_data_scaled"]}'
camera = config["camera"]
savepath = f'{output_path}/{config["reprojection"]["path"]}'
os.makedirs(savepath, exist_ok=True)
savename = f'{savepath}/{config["reprojection"]["file"]}'

with open(sfm_path, 'r') as recosntruction:
    sfm_data = json.load(recosntruction)
recosntruction.close

f = sfm_data["intrinsics"][0]["value"]["ptr_wrapper"]["data"]["focal_length"]
ppx = sfm_data["intrinsics"][0]["value"]["ptr_wrapper"]["data"]["principal_point"][0]
ppy = sfm_data["intrinsics"][0]["value"]["ptr_wrapper"]["data"]["principal_point"][1]
kmatrix = np.array([[f, 0, ppx],[0, f, ppy],[0, 0, 1]])

pix_err_x = []
pix_err_y = []

print(f'Running reprojection for {len(sfm_data["structure"])} points')
for poses in sfm_data["extrinsics"]:
    # Camera pose
    R = np.array(poses["value"]["rotation"])
    c = np.array(poses["value"]["center"])
    # Translation vector and Extrinsic Matrix
    t = -np.dot(R,c)
    Rt = np.hstack((R, t.reshape(-1, 1)))
    for point in sfm_data["structure"]:
        pos = 0
        for feat in point["value"]["observations"]:
            if feat["key"] == poses["key"]:
                # 3D point coordinates
                cloud_point = np.array(point["value"]["X"])
                # Reprojection Equations
                point_3d = np.append(cloud_point, 1)
                P = np.dot(kmatrix, Rt)
                point_2d = np.dot(P, point_3d)
                point_2d /= point_2d[2]
                diff_x = feat["value"]["x"][0]-point_2d[0]
                diff_y = feat["value"]["x"][1]-point_2d[1]
                # Create new variable in the sfm_data file
                point["value"]["observations"][pos]["reprojection"] = {
                    "x": point_2d[:2].tolist(),
                    "error": [diff_x, diff_y]
                }
                pix_err_x.append(diff_x)
                pix_err_y.append(diff_y)
                pos += 1
            else:
                pos += 1
                continue

# Once the JSON is completed some statistics are computed
sfm_data["Reprojection Statistics"] = {
    "Mean error in x-axis (pixels)": statistics.mean(pix_err_x),
    "Mean error in y-axis (pixels)": statistics.mean(pix_err_y),
    "Error std in x-axis (pixels)": statistics.stdev(pix_err_x),
    "Error std in y-axis (pixels)": statistics.stdev(pix_err_y),
    "Max error in x-axis (pixels)": max(pix_err_x),
    "Max error in y-axis (pixels)": max(pix_err_y),
    "Min error in x-axis (pixels)": min(pix_err_x),
    "Min error in y-axis (pixels)": min(pix_err_y)
}

print(f'Saving results in {savepath}')
with open(savename, 'w') as reproj:
    json.dump(sfm_data, reproj, indent=4)
reproj.close

# Plot Pixel info in x
sns.histplot(pix_err_x, kde=True, color='blue')
plt.title('Pixel error on the x-axis distribution')
plt.xlabel('Value')
plt.ylabel('Density')
plt.savefig(f'{savepath}/pix_err_x.png')
plt.close()

# Plot Pixel info in y
sns.histplot(pix_err_y, kde=True, color='blue')
plt.title('Pixel error on the y-axis distribution')
plt.xlabel('Value')
plt.ylabel('Density')
plt.savefig(f'{savepath}/pix_err_y.png')
plt.close()

print(f'Reprojection study succesfully finished')