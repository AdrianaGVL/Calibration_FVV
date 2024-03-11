# Libraries
import json

# file Path
dataset_path = '/media/agv/JesusGTI/Calibration/iPhone_Recordings/C_chess/frames/output'
mvg_results_path = f'{dataset_path}/Reconstruction'
sfm_data_file = f'{mvg_results_path}/sfm_data.json'
cv_file = f'{dataset_path}/openCV_coords_acc.json'
savepath = f'{dataset_path}/3D_chesspoints_acc_0_05.json'

# Read JSON files
sfm_data = ''
opencv_data = ''
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close
with open(cv_file) as f:
    opencv_data = json.load(f)
f.close

# Pixel range, computation errors
errR = 0.05
possible_point = False

# JSON structure
#Points in common MVG & CV
common = {
    "Filename": '',
    "Frame key": '',
    "Coords 2D MVG": [],
    "Coords CV": []
}
# 3D Coordinate info
coords_3D_2D = {
    "Coordinate key": '',
    "Coords 3D": [],
    "OpenMVG-OpenCV": []
}
# Main file
points_CV_MVG= {
    "Record": 'C_Chess',
    "Camera": 'iPhone XS Max',
    "Coordinates": []
}
frames_mvg = []
frames_cv = []
frames = []
coords_cv = []

# Some frames are not in the OpenCV file
for chessboard in opencv_data["Corners"]:
    frames_cv.append(chessboard["filename"])
        
for view in sfm_data["views"]:
    aux = view["value"]["ptr_wrapper"]["data"]["filename"]        

    # Index to obtain the 3D coordinate if its all ready listed.
    try:
        match = frames_cv.index(aux)
    except:
        match = 'None'

    if type(match) == int: 
        frames_mvg.append(view["key"])
        frames.append(view["value"]["ptr_wrapper"]["data"]["filename"])
        coords_cv.append(opencv_data["Corners"][match]["x"])

# Chessboard search in sfm_data file
with open(savepath, 'w') as f:
    for k in range(len(sfm_data["structure"])):
        for m in range(len(sfm_data["structure"][k]["value"]["observations"])):

            aux2 = sfm_data["structure"][k]["value"]["observations"][m]["key"]
            try:
                valid_frame = frames_mvg.index(aux2)
            except:
                valid_frame = 'None'

            if type(valid_frame) != int:
                continue
            else:
                possible_point = False
                coords2D_mvg = sfm_data["structure"][k]["value"]["observations"][m]["value"]["x"]
                coord_3D = sfm_data["structure"][k]["value"]["X"]
                key_3D = sfm_data["structure"][k]["key"]
                frame_key = frames_mvg[valid_frame]
                frame = frames[valid_frame]
                coords_frame = coords_cv[valid_frame]

                for j in range(len(coords_frame)):
                    diff_xs = abs(float(coords_frame[j][0]) - coords2D_mvg[0])
                    diff_ys = abs(float(coords_frame[j][1]) - coords2D_mvg[1])
                    if (diff_xs <= errR) and (diff_ys <= errR):
                        common["Filename"] = frame
                        common["Frame key"] = frame_key
                        common["Coords 2D MVG"] = coords2D_mvg
                        common["Coords CV"].append(coords_frame[j])
                        possible_point = True
                    else:
                        continue

                if possible_point:
                    coords_3D_2D["Coordinate key"] = key_3D
                    coords_3D_2D["Coords 3D"].append(coord_3D)
                    coords_3D_2D["OpenMVG-OpenCV"].append(common.copy())
                    common["Coords CV"] = []
                else:
                    continue
                        
        if possible_point:
            points_CV_MVG["Coordinates"].append(coords_3D_2D.copy())
            coords_3D_2D["OpenMVG-OpenCV"] = []
            coords_3D_2D["Coords 3D"] = []

    print('Writing')
    json.dump(points_CV_MVG, f, indent=4)
f.close
