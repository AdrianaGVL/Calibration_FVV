#######################
#  Created on: April 1, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import yaml
import statistics
import math
import copy
import matplotlib.pyplot as plt
import seaborn as sns
import os
import cv2
import numpy as np

# Config file
with open('./config_file.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Paths
camera = config["camera"]
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
# App paths
reconstruction_known = f'{output_path}/{config["ckecker_path"]}'
scale_info = f'{output_path}/{config["scale_data"]}'
os.makedirs(scale_info, exist_ok=True)
# App files
sfm_data_file = f'{reconstruction_known}/{config["checker_sfm_data"]}'
chess_measures_file = f'{scale_info}/{config["measures_file"]}'
version = ''

# Number or corners along the x axes and y axes
nCorners_x = 10
nCorners_y = 5
last = [nCorners_x * i for i in range(nCorners_y+1)]


# Distance in real life (mm)
if scene == f'{main_path}/Video_Chess_C':
    dist = 28
elif scene == f'{main_path}/Video_Chess_D':
    dist = 101.6

# JSON Structure
measures = {
    "Scene": scene,
    "Measures":{
        "Scaling Factor":{
            "Mean": '',
            "Standard deviation": '',
            "Max. value": '',
            "Min. value": ''
        },
        "Error distance between reconstructed values and real ones in the X-axis":{
            "Mean": '',
            "Standard deviation": '',
            "Max. value": '',
            "Min. value": ''
        },
        "Error distance between reconstructed values and real ones in the Y-axis":{
            "Mean": '',
            "Standard deviation": '',
            "Max. value": '',
            "Min. value": ''
        },
        "Angles in x axis":{
            "Mean": '',
            "Standard deviation": '',
            "Max. value": '',
            "Min. value": ''
        },
        "Angles in y axis":{
            "Mean": '',
            "Standard deviation": '',
            "Max. value": '',
            "Min. value": ''
        }
    },
    "Measures per point": []
}
distance = {
    "X axis data":{
        "Reference point": '',
        "Adjacent point": '',
        "distance" : '',
        "Angle": '',
        "Scale": ''
    },
    "Y axis data":{
        "Adjacent point": '',
        "distance" : '',
        "Scale": '',
        "Angle": ''
    }
}

# Read the reconstruction data
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

points_3D = []
num_points = len(sfm_data["structure"])
for coords in sfm_data["structure"]:
    x_point = coords["value"]["X"][0]
    y_point = coords["value"]["X"][1]
    point_3D = (x_point, y_point)
    points_3D.append(point_3D)

scales = []
errors_distance_x = []
errors_distance_y = []
errors_distance_total = []
angles_x = []
angles_y = []
pos_aux = 0
for i in range(len(points_3D)):
    if i in last:
        pos_aux +=1

    if i != ((nCorners_x*pos_aux)-1):
        dist_x = points_3D[i][0] - points_3D[i+1][0]
        dist_y = points_3D[i][1] - points_3D[i+1][1]

        scale_x = abs(dist/dist_x) # Scale in the corresponding (dist) units
        angle_x = math.degrees(math.atan(dist_y/dist_x)) # Will return a negative value if clockwise
        distance["X axis data"]["Reference point"] = i
        distance["X axis data"]["Adjacent point"] = i+1
        distance["X axis data"]["distance"] = abs(dist_x)
        distance["X axis data"]["Scale"] = scale_x
        if version == '_mm':
            error_distance = scale_x - 1.0000000
            errors_distance_x.append(error_distance)
            errors_distance_total.append(error_distance)
        distance["X axis data"]["Angle"] = angle_x
        scales.append(scale_x)
        angles_x.append(angle_x)
    else:
        dist_x = 0
        distance["X axis data"]["Reference point"] = i
        distance["X axis data"]["Adjacent point"] = 'No adjacent point'
        distance["X axis data"]["distance"] = 'NaN'
        distance["X axis data"]["Scale"] = 'NaN'
        distance["X axis data"]["Angle"] = 'NaN'

    if i <= ((nCorners_x*nCorners_y)-(1+nCorners_x)):
        dist_y = points_3D[i][1] - points_3D[i+nCorners_x][1]
        dist_x = points_3D[i][0] - points_3D[i+nCorners_x][0]
        scale_y = abs(dist/dist_y) # Scale in the corresponding (dist) units
        angle_y = math.degrees(math.atan(dist_x/dist_y))
        distance["Y axis data"]["Reference point"] = i
        distance["Y axis data"]["Adjacent point"] = i+nCorners_x
        distance["Y axis data"]["distance"] = abs(dist_y)
        distance["Y axis data"]["Scale"] = scale_y
        if version == '_mm':
            error_distance = scale_y - 1.0000000
            errors_distance_y.append(error_distance)
            errors_distance_total.append(error_distance)
        distance["Y axis data"]["Angle"] = angle_y
        scales.append(scale_y)
        angles_y.append(angle_y)
    else:
        dist_y = 0
        distance["Y axis data"]["Reference point"] = i
        distance["Y axis data"]["Adjacent point"] = 'No adjacent point'
        distance["Y axis data"]["distance"] = 'NaN'
        distance["Y axis data"]["Scale"] = 'NaN'
        distance["Y axis data"]["Angle"] = 'NaN'

    measures["Measures per point"].append(copy.deepcopy(distance))

measures["Measures"]["Scaling Factor"]["Mean"] = statistics.mean(scales)
measures["Measures"]["Scaling Factor"]["Standard deviation"] = statistics.stdev(scales)
measures["Measures"]["Scaling Factor"]["Max. value"] = max(scales)
measures["Measures"]["Scaling Factor"]["Min. value"] = min(scales)

if version == '_mm':
    measures["Measures"]["Error distance between reconstructed values and real ones in the X-axis"]["Mean"] = statistics.mean(errors_distance_x)
    measures["Measures"]["Error distance between reconstructed values and real ones in the X-axis"]["Standard deviation"] = statistics.stdev(errors_distance_x)
    measures["Measures"]["Error distance between reconstructed values and real ones in the X-axis"]["Max. value"] = max(errors_distance_x)
    measures["Measures"]["Error distance between reconstructed values and real ones in the X-axis"]["Min. value"] = min(errors_distance_x)

    measures["Measures"]["Error distance between reconstructed values and real ones in the Y-axis"]["Mean"] = statistics.mean(errors_distance_y)
    measures["Measures"]["Error distance between reconstructed values and real ones in the Y-axis"]["Standard deviation"] = statistics.stdev(errors_distance_y)
    measures["Measures"]["Error distance between reconstructed values and real ones in the Y-axis"]["Max. value"] = max(errors_distance_y)
    measures["Measures"]["Error distance between reconstructed values and real ones in the Y-axis"]["Min. value"] = min(errors_distance_y)

measures["Measures"]["Angles in x axis"]["Mean"] = statistics.mean(angles_x)
measures["Measures"]["Angles in x axis"]["Standard deviation"] = statistics.stdev(angles_x)
measures["Measures"]["Angles in x axis"]["Max. value"] = max(angles_x)
measures["Measures"]["Angles in x axis"]["Min. value"] = min(angles_x)

measures["Measures"]["Angles in y axis"]["Mean"] = statistics.mean(angles_y)
measures["Measures"]["Angles in y axis"]["Standard deviation"] = statistics.stdev(angles_y)
measures["Measures"]["Angles in y axis"]["Max. value"] = max(angles_y)
measures["Measures"]["Angles in y axis"]["Min. value"] = min(angles_y)

with open(chess_measures_file, 'w') as pqs:
    json.dump(measures, pqs, indent=4)
pqs.close

# Plot Scale info
if version == '_mm':
    norm_scale = errors_distance_total
else:
    mean_scale = statistics.mean(scales)
    norm_scale = [value / mean_scale for value in scales]
sns.histplot(norm_scale, kde=True, color='blue')
hist, bin_edges = np.histogram(scales, bins='auto')
# print(bin_edges)
if version == '_mm':
    plt.title('Error distribution')
    plt.xlabel('Error')
else:
    plt.title('Scales distribution')
    plt.xlabel('Value')
plt.ylabel('Density')
plt.savefig(f'{scale_info}/Distribution_distance{version}.png')
# plt.show()
plt.close()

if version == '_mm':
    # Plot Error in x info
    sns.histplot(errors_distance_x, kde=True, color='blue')
    hist, bin_edges = np.histogram(scales, bins='auto')
    # print(bin_edges)
    plt.title('Error distance between reconstructed values and real ones in the X-axis')
    plt.xlabel('Error')
    plt.ylabel('Density')
    plt.savefig(f'{scale_info}/Error_distance_x{version}.png')
    # plt.show()
    plt.close()

    # Plot Error in y info
    sns.histplot(errors_distance_y, kde=True, color='blue')
    hist, bin_edges = np.histogram(scales, bins='auto')
    # print(bin_edges)
    plt.title('Error distance between reconstructed values and real ones in the Y-axis')
    plt.xlabel('Error')
    plt.ylabel('Density')
    plt.savefig(f'{scale_info}/Error_distance_y{version}.png')
    # plt.show()
    plt.close()


# Plot Angle x info
# psx_values = [abs(value) for value in angles_x]
sns.histplot(angles_x, kde=True, color='blue')
plt.title('Angles on the x-axis distribution')
plt.xlabel('Value')
plt.ylabel('Density')
plt.savefig(f'{scale_info}/Distribution_angles_x{version}.png')
# plt.show()
plt.close()

# Plot Angle y info
# psy_values = [abs(value) for value in angles_y]
sns.histplot(angles_y, kde=True, color='blue')
plt.title('Angles on the y-axis distribution')
plt.xlabel('Value')
plt.ylabel('Density')
plt.savefig(f'{scale_info}/Distribution_angles_y{version}.png')
# plt.show()
plt.close()

# # Points far away from the mean and high error
# positions = [index for index, value in enumerate(scales) if 1.005 <= value <= 1.010]
# point_positions = [math.floor(valor / 2) for valor in positions]
# # Plot points
# frame = cv2.imread(frame_path)
# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# fconers, corners = cv2.findChessboardCorners(gray, (nCorners_x, nCorners_y), cv2.CALIB_CB_EXHAUSTIVE + cv2.CALIB_CB_ACCURACY)
# corners_filered = [corners[pos] for pos in point_positions]
# for pos in point_positions:
#    cv2.drawChessboardCorners(frame, (nCorners_x, nCorners_y), np.array(corners_filered), False)
# cv2.imwrite('Results/Images/Statistics/Points_out_of_the_mean.png', frame)