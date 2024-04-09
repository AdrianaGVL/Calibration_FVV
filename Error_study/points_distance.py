#######################
#  Created on: April 1, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import statistics

# Paths
main_path = '/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
scene_path = f'{main_path}/Video_Chess_C'
results_path = f'{scene_path}/output_chiquito'
sfm_data_file = f'{results_path}/Reconstruction_for_known/cloud_and_poses.json'
chess_measures_path = f'{results_path}/measures_chess.json'

# Number or corners along the x axes and y axes
nCorners_x = 8
nCorners_y = 6
last = [nCorners_x * i for i in range(nCorners_y+1)]


# Distance in real life (m)
if scene_path == f'{main_path}/Video_Chess_C':
    dist = 0.028
elif scene_path == f'{main_path}/Video_Chess_D':
    dist = 0.301

# JSON Structure
measures = {
    "Scene": '',
    "Measures": [],
    "Mean scaling factor": '',
    "Standard deviation": '',
    "Max. scaling value": '',
    "Min. scaling value": ''

}
distance = {
    "Reference point": '',
    "Adjacent point in x axis": '',
    "distance in x axis" : '',
    "Scale in x axis": '',
    "Adjacent point in y axis": '',
    "distance in y axis" : '',
    "Scale in y axis": ''
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
pos_aux = 0
for i in range(len(points_3D)):
    if i in last:
        pos_aux +=1

    if i != ((nCorners_x*pos_aux)-1):
        dist_x = points_3D[i][0] - points_3D[i+1][0]
        distance["Reference point"] = i
        distance["Adjacent point in x axis"] = i+1
        distance["distance in x axis"] = dist_x
        distance["Scale in x axis"] = abs(dist_x/dist)
        scales.append(abs(dist_x/dist))
    else:
        dist_x = 0
        distance["Reference point"] = i
        distance["Adjacent point in x axis"] = 'No adjacent point'
        distance["distance in x axis"] = 'NaN'
        distance["Scale in x axis"] = 'NaN'

    if i <= ((nCorners_x*nCorners_y)-(1+nCorners_x)):
        dist_y = abs(points_3D[i][1] - points_3D[i+nCorners_x][1])
        distance["Reference point"] = i
        distance["Adjacent point in y axis"] = i+nCorners_x
        distance["distance in y axis"] = dist_y
        distance["Scale in y axis"] = abs(dist_y/dist)
        scales.append(abs(dist_y/dist))
    else:
        dist_y = 0
        distance["Reference point"] = i
        distance["Adjacent point in y axis"] = 'No adjacent point'
        distance["distance in y axis"] = 'NaN'
        distance["Scale in y axis"] = 'NaN'
    
    measures["Measures"].append(distance.copy())

measures["Mean scaling factor"] = statistics.mean(scales)
measures["Standard deviation"] = statistics.stdev(scales)
measures["Max. scaling value"] = max(scales)
measures["Min. scaling value"] = min(scales)

with open(f'{results_path}/measures_chess.json', 'w') as pqs:
    json.dump(measures, pqs, indent=4)
pqs.close