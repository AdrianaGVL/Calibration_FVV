#######################
#  Created on: April 1, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import statistics
import math

# Paths
scene = 'Video_Chess_D'
main_path = '/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
scene_path = f'{main_path}/{scene}'
results_path = f'{scene_path}/output'
sfm_data_file = f'{results_path}/Reconstruction_for_known/cloud_and_poses.json'
chess_measures_path = f'{results_path}/measures_chess.json'

# Number or corners along the x axes and y axes
nCorners_x = 10
nCorners_y = 5
last = [nCorners_x * i for i in range(nCorners_y+1)]


# Distance in real life (m)
if scene_path == f'{main_path}/Video_Chess_C':
    dist = 0.028
elif scene_path == f'{main_path}/Video_Chess_D':
    dist = 0.301

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
        },
        "Plane data":{
            "Equation": '',
            "Mean error": '',
            "Standard deviation": '',
            "Max. error value": '',
            "Mix. error value": ''
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
        scale_x = abs(dist_x/dist)
        angle_x = math.degrees(math.atan2(dist_x, dist_y))
        distance["X axis data"]["Reference point"] = i
        distance["X axis data"]["Adjacent point"] = i+1
        distance["X axis data"]["distance"] = dist_x
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
        scale_y = abs(dist_y/dist)
        angle_y = math.degrees(math.atan2(dist_x, dist_y))
        distance["Y axis data"]["Reference point"] = i
        distance["Y axis data"]["Adjacent point"] = i+nCorners_x
        distance["Y axis data"]["distance"] = dist_y
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

    
    measures["Measures per point"].append(distance.copy())

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

with open(f'{results_path}/measures_chess.json', 'w') as pqs:
    json.dump(measures, pqs, indent=4)
pqs.close