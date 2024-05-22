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
import cv2
import numpy as np

# Config file
with open('./config_file.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Parameters & directories
camera = config["camera"]
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
# App paths
sfm_data_file = f'{output_path}/{config["sfm_data_scaled"]}'
results_path = f'{output_path}/{config["scale_data"]}'
# App files
jsons_path = './jsons_structures.json'
measures_file = f'{results_path}/{config["measures_file"]}'

# Number or corners along the x axes and y axes
nCorners_x = config["num_corners_x"]
nCorners_y = config["num_corners_y"]
last = [nCorners_x * i for i in range(nCorners_y+1)]

# Distance in real life (mm)
dist = config["dist_mm"]

# JSON Structure
# Read the reconstruction data
with open(jsons_path) as j:
    json_model = json.load(j)
j.close

measures = json_model["Measures"]
distance = json_model["Distance_info"]

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
        # Distance error
        distance["X axis data"]["Reference point"] = i
        distance["X axis data"]["Adjacent point"] = i+1
        dist_x = points_3D[i][0] - points_3D[i+1][0]
        dist_y = points_3D[i][1] - points_3D[i+1][1]
        distance["X axis data"]["distance"] = abs(dist_x)
        error_x = abs(dist_x) - dist
        distance["X axis data"]["error in distance"] = error_x
        errors_distance_x.append(error_x)
        errors_distance_total.append(error_x)

        # Angles error
        angle_x = math.degrees(math.atan(dist_y/dist_x)) # Will return a negative value if clockwise
        distance["X axis data"]["Angle"] = angle_x
        angles_x.append(angle_x)
    else:
        dist_x = 0
        distance["X axis data"]["Reference point"] = i
        distance["X axis data"]["Adjacent point"] = 'No adjacent point'
        distance["X axis data"]["distance"] = 'NaN'
        distance["X axis data"]["Scale"] = 'NaN'
        distance["X axis data"]["Angle"] = 'NaN'

    if i <= ((nCorners_x*nCorners_y)-(1+nCorners_x)):
        # Distance error
        distance["Y axis data"]["Reference point"] = i
        distance["Y axis data"]["Adjacent point"] = i+nCorners_x
        dist_y = points_3D[i][1] - points_3D[i+nCorners_x][1]
        dist_x = points_3D[i][0] - points_3D[i+nCorners_x][0]
        distance["Y axis data"]["distance"] = abs(dist_y)
        error_y = abs(dist_y) - dist
        distance["Y axis data"]["error in distance"] = error_y
        errors_distance_x.append(error_y)
        errors_distance_total.append(error_y)

        # Angles error
        angle_y = math.degrees(math.atan(dist_x/dist_y))
        distance["Y axis data"]["Angle"] = angle_y
        angles_y.append(angle_y)
    else:
        dist_y = 0
        distance["Y axis data"]["Reference point"] = i
        distance["Y axis data"]["Adjacent point"] = 'No adjacent point'
        distance["Y axis data"]["distance"] = 'NaN'
        distance["Y axis data"]["Scale"] = 'NaN'
        distance["Y axis data"]["Angle"] = 'NaN'

    measures["Measures per point"].append(copy.deepcopy(distance))


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

with open(measures_file, 'w') as pqs:
    json.dump(measures, pqs, indent=4)
pqs.close

# Plot Error in x info
sns.histplot(errors_distance_x, kde=True, color='blue')
hist, bin_edges = np.histogram(errors_distance_x, bins='auto')
# print(bin_edges)
plt.title('Error distance between reconstructed values and real ones in the X-axis')
plt.xlabel('Error (mm)')
plt.ylabel('Density (nº 3D points)')
plt.savefig(f'{results_path}/Error_distance_x.png')
plt.close()

# Plot Error in y info
sns.histplot(errors_distance_y, kde=True, color='blue')
hist, bin_edges = np.histogram(errors_distance_y, bins='auto')
# print(bin_edges)
plt.title('Error distance between reconstructed values and real ones in the Y-axis')
plt.xlabel('Error (mm)')
plt.ylabel('Density (nº 3D points)')
plt.savefig(f'{results_path}/Error_distance_y.png')
plt.close()

# Plot Error in both axis
sns.histplot(errors_distance_total, kde=True, color='blue')
hist, bin_edges = np.histogram(errors_distance_total, bins='auto')
# print(bin_edges)
plt.title('Error distance between reconstructed values and real ones')
plt.xlabel('Error (mm)')
plt.ylabel('Density (nº 3D points)')
plt.savefig(f'{results_path}/Error_distance.png')
plt.close()


# Plot Angle x info
# psx_values = [abs(value) for value in angles_x]
sns.histplot(angles_x, kde=True, color='blue')
plt.title('Angles on the x-axis distribution')
plt.xlabel('Value (º)')
plt.ylabel('Density (nº 3D points)')
plt.savefig(f'{results_path}/Distribution_angles_x.png')
plt.close()

# Plot Angle y info
# psy_values = [abs(value) for value in angles_y]
sns.histplot(angles_y, kde=True, color='blue')
plt.title('Angles on the y-axis distribution')
plt.xlabel('Value (º)')
plt.ylabel('Density (nº 3D points)')
plt.savefig(f'{results_path}/Distribution_angles_y.png')
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