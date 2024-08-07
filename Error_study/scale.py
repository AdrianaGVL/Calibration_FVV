#######################
#  Created on: April 1, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import yaml
import statistics
import copy
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
sys.path.append(os.getcwd())
import numpy as np
from utils_py import analysis_tools as aly

# Config file
config_f =  sys.argv[1]
with open(config_f, 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Paths
camera = config["camera"]
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
# App paths
reconstruction_known = f'{output_path}/{config["known_poses"]}'
results_path = f'{output_path}/{config["scale_data"]}'
os.makedirs(results_path, exist_ok=True)
# App files
jsons_path = './jsons_structures.json'
sfm_data_file = f'{reconstruction_known}/{config["known_sfm_data"]}'
scales_data = f'{results_path}/{config["scales_file"]}'

# Number or corners along the x axes and y axes
nCorners_x = config["num_corners_x"]
nCorners_y = config["num_corners_y"]
last = [nCorners_x * i for i in range(nCorners_y+1)]

# Distance in real life (mm)
dist = config["dist_mm"]
dist_rlx = aly.eu_dis([0, 0, 0], [101.6, 0, 0])
dist_rly = aly.eu_dis([0, 0, 0], [0, 101.6, 0])
# JSON Structure
# Read the reconstruction data
with open(jsons_path) as j:
    json_model = json.load(j)
j.close

scale = json_model["Scales"]
scale_ax = json_model["Scale_info"]

# Read the reconstruction data
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

points_3D = []
num_points = len(sfm_data["structure"])
key = 0
while len(points_3D) != num_points:
    for coords in sfm_data["structure"]:
        if key == coords["key"]:
            x_point = coords["value"]["X"][0]
            y_point = coords["value"]["X"][1]
            z_point = coords["value"]["X"][2]
            point_3D = (x_point, y_point, z_point)
            points_3D.append(point_3D)
            key +=1
        else:
            continue

scales = []
scales_x = []
scales_y = []
pos_aux = 0
for i in range(len(points_3D)):
    if i in last:
        pos_aux +=1

    if i != ((nCorners_x*pos_aux)-1):
        scale_ax["X axis data"]["Reference point"] = i
        scale_ax["X axis data"]["Adjacent point"] = i+1
        dist_x = aly.eu_dis(points_3D[i], points_3D[i+1])
        print(f'3D coordinates: {points_3D[i]} - {points_3D[i+1]}')
        print(f'Distance OpenMVG point: {dist_x}')
        print(f'Distance real life: {dist_rlx}')
        # dist_x = points_3D[i][0] - points_3D[i+1][0]
        scale_x = dist_rlx/dist_x # Scale in the corresponding (dist) units
        print(f'Scale: {scale_x}')
        scale_ax["X axis data"]["Scale"] = scale_x
        scales.append(scale_x)
        scales_x.append(scale_x)
    else:
        dist_x = 0
        scale_ax["X axis data"]["Reference point"] = i
        scale_ax["X axis data"]["Adjacent point"] = 'No adjacent point'
        scale_ax["X axis data"]["Scale"] = 'NaN'

    if i <= ((nCorners_x*nCorners_y)-(1+nCorners_x)):
        scale_ax["Y axis data"]["Reference point"] = i
        scale_ax["Y axis data"]["Adjacent point"] = i+nCorners_x
        dist_y = aly.eu_dis(points_3D[i], points_3D[i+nCorners_x])
        # dist_y = points_3D[i][1] - points_3D[i+nCorners_x][1]
        scale_y = dist_rly/dist_y # Scale in the corresponding (dist) units
        scale_ax["Y axis data"]["Scale"] = scale_y
        scales.append(scale_y)
        scales_y.append(scale_y)
    else:
        dist_y = 0
        scale_ax["Y axis data"]["Reference point"] = i
        scale_ax["Y axis data"]["Adjacent point"] = 'No adjacent point'
        scale_ax["Y axis data"]["Scale"] = 'NaN'

    scale["Measures per point"].append(copy.deepcopy(scale_ax))

# statistics_scales = [abs(value) for value in scales]
scale["Scaling Factor"]["Mean"] = aly.mae_study(scales)[0]
scale["Scaling Factor"]["Standard deviation"] = aly.mae_study(scales)[1]
scale["Scaling Factor"]["Max. value"] = max(scales)
scale["Scaling Factor"]["Min. value"] = min(scales)

with open(scales_data, 'w') as pqs:
    json.dump(scale, pqs, indent=4)
pqs.close

# Plot Scale info
sns.histplot(scales, kde=True, color='blue')
# hist, bin_edges = np.histogram(scales, bins='auto')
# print(bin_edges)
plt.title('Scales distribution')
plt.xlabel('Scale value')
plt.ylabel('Density (nº 3D points)')
plt.savefig(f'{results_path}/Scales_distribution.png')
plt.close()

# Plot Error in x info
sns.histplot(scales_x, kde=True, color='blue')
# hist, bin_edges = np.histogram(scales_x, bins='auto')
# print(bin_edges)
plt.title('Scales distribution in the X-axis')
plt.xlabel('Scale value')
plt.ylabel('Density (nº 3D points)')
plt.savefig(f'{results_path}/Scales_distribution_x.png')
plt.close()

# Plot Error in y info
sns.histplot(scales_y, kde=True, color='blue')
# hist, bin_edges = np.histogram(scales_y, bins='auto')
# print(bin_edges)
plt.title('Scales distribution in the Y-axis')
plt.xlabel('Scale value')
plt.ylabel('Density (nº 3D points)')
plt.savefig(f'{results_path}/Scales_distribution_y.png')
plt.close()