#######################
#  Created on: April 1, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import statistics
import math
import copy
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
import numpy as np

# Paths
scene = 'Video_Chess_D'
version = '' # Nothing ('') or '_mm'
main_path = '/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
scene_path = f'{main_path}/{scene}'
results_path = f'{scene_path}/output'
sfm_data_file = f'{results_path}/Reconstruction_for_known/cloud_and_poses{version}.json'
chess_measures_file = f'{results_path}/measures_chess{version}.json'
frame_path = f'{scene_path}/frames/frame_29.png'

# Number or corners along the x axes and y axes
nCorners_x = 10
nCorners_y = 5
last = [nCorners_x * i for i in range(nCorners_y+1)]


# Distance in real life (mm)
if scene_path == f'{main_path}/Video_Chess_C':
    dist = 28
elif scene_path == f'{main_path}/Video_Chess_D':
    dist = 301

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
for coords in sfm_data["structure"]:
    x_point = coords["value"]["X"][0]
    y_point = coords["value"]["X"][1]
    point_3D = (x_point, y_point)
    points_3D.append(point_3D)

scales = []
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
        angle_x = math.degrees(math.atan2(dist_x, dist_y)) # Will return a negative value if clockwise
        distance["X axis data"]["Reference point"] = i
        distance["X axis data"]["Adjacent point"] = i+1
        distance["X axis data"]["distance"] = abs(dist_x)
        distance["X axis data"]["Scale"] = scale_x
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
        angle_y = math.degrees(math.atan2(dist_y, dist_x))
        distance["Y axis data"]["Reference point"] = i
        distance["Y axis data"]["Adjacent point"] = i+nCorners_x
        distance["Y axis data"]["distance"] = abs(dist_y)
        distance["Y axis data"]["Scale"] = scale_y
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
mean_scale = statistics.mean(scales)
norm_scale = [value / mean_scale for value in scales]
sns.histplot(norm_scale, kde=True, color='blue')
hist, bin_edges = np.histogram(scales, bins='auto')
print(bin_edges)
plt.title('Scales distribution')
plt.xlabel('Value')
plt.ylabel('Density')
plt.savefig(f'Results/Images/Statistics/Distribution_distance{version}.png')
# plt.show()
plt.close()


# Plot Angle x info
psx_values = [abs(value) for value in angles_x]
sns.histplot(psx_values, kde=True, color='blue')
plt.title('Angles on the x-axis distribution')
plt.xlabel('Value')
plt.ylabel('Density')
plt.savefig(f'Results/Images/Statistics/Distribution_angles_x{version}.png')
# plt.show()
plt.close()

# Plot Angle y info
psy_values = [abs(value) for value in angles_y]
sns.histplot(psy_values, kde=True, color='blue')
plt.title('Angles on the y-axis distribution')
plt.xlabel('Value')
plt.ylabel('Density')
plt.savefig(f'Results/Images/Statistics/Distribution_angles_y{version}.png')
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