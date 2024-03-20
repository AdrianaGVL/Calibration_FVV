#Libraries
import cv2
import glob
import time
import os
from natsort import natsorted
import numpy as np
import json

# Paths
main_path = '/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
scene_path = f'{main_path}/frames'
results_path = f'{main_path}/output'
sfm_data_file = f'{results_path}/sfm_data_no_info.json'
drawn_corners_path = f'{results_path}/frames_with_corners_opencv'
features_path = f'{results_path}/matches_for_known'
os.makedirs(features_path, exist_ok=True)

# Save Images with drawn corners?
img_with_corners = False
img_corners_show = False    # Print every image with its drawn corners for 3s (can be change to wait key)

# Number or corners along the x axes and y axes
nCorners_x = 10
nCorners_y = 5

# List the images (frames in this case)
chess_images = natsorted(glob.glob(f'{scene_path}/IMG_4146.jpeg'))
objpoints = []
imgpoints = []

# ID given by OpenMVG
sfm_data = ''
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

feats = []
filenames = []
ids = []
for view in sfm_data["views"]:
    filename = view["value"]["ptr_wrapper"]["data"]["filename"]
    filenames.append(filename)
    id = view["value"]["ptr_wrapper"]["data"]["id_view"]
    ids.append(id)

# Loop to iterate along all the images
for i in range(len(chess_images)):
    # Read in the image
    chess_board_image = cv2.imread(chess_images[i])
    file = os.path.basename(chess_images[i])
    file_file = file.split('.')[0]
    print(f'File: {file}')
    # Convert to grayscale
    gray = cv2.cvtColor(chess_board_image, cv2.COLOR_RGB2GRAY)
    height, width = chess_board_image.shape[:2]
    # images.append(gray)
    # Find the chessboard corners
    fconers, corners = cv2.findChessboardCorners(gray, (nCorners_x, nCorners_y), cv2.CALIB_CB_EXHAUSTIVE + cv2.CALIB_CB_ACCURACY)

    # If found, draw corners
    if fconers:

        if img_with_corners:
            os.makedirs(drawn_corners_path, exist_ok=True)
            # Draw the corners
            cv2.drawChessboardCorners(chess_board_image, (nCorners_x, nCorners_y), corners, fconers) #(nCorners_x, nCorners_y)
            cv2.imwrite(f'{drawn_corners_path}/IMG_{str(i)}.png', chess_board_image)
            if img_corners_show:
                cv2.imshow(f'{file} with corners',chess_board_image)
                time.sleep(20)   #cv2.waitKey()

        # # .feat and .desc files are created
        # with open(f'{features_path}/{file_file}.feat', 'w') as f:
        #     for coord in corners:
        #         f.write(f'{coord[0][0]} {coord[0][1]}\n')
        # f.close
                
        feats.append(file)

        objp = np.zeros((nCorners_y*nCorners_x, 3), np.float32)
        objp[:, :2] = np.mgrid[0:nCorners_x, 0:nCorners_y].T.reshape(-1, 2)
        objpoints.append(objp)
        imgpoints.append(corners)
    
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (width, height), None, None)
focal_length = mtx[0, 0]
k1, k2, k3, p1, p2 = dist.ravel()
p_p, dist_k3 = [], []
p_p.append(mtx[0, 2])
p_p.append(mtx[1, 2])
dist_k3.append(k1)
dist_k3.append(k2)
dist_k3.append(k3)
sfm_data["intrinsics"][0]["value"]["ptr_wrapper"]["data"]["focal_length"] = focal_length
sfm_data["intrinsics"][0]["value"]["ptr_wrapper"]["data"]["principal_point"] = p_p
sfm_data["intrinsics"][0]["value"]["ptr_wrapper"]["data"]["disto_k3"] = dist_k3

o = len(imgpoints)
for i in range(len(imgpoints)):
    pose = {
        "key": '',
        "value": {
            "rotation": [],
            "center": []
        }
    }
    matrices = []
    center = []
    ret, rvec, tvec = cv2.solvePnP(objpoints[i], imgpoints[i], mtx, dist)
    rvec = np.array(rvec).reshape(-1)
    # OpenMVG gives rotation for each axis.
    R_x = np.eye(3)
    R_y = np.eye(3)
    R_z = np.eye(3)
    cv2.Rodrigues(np.array([[1, 0, 0]]) * rvec[0], R_x)
    matrices.append(R_x.tolist())
    cv2.Rodrigues(np.array([[0, 1, 0]]) * rvec[1], R_y)
    matrices.append(R_y.tolist())
    cv2.Rodrigues(np.array([[0, 0, 1]]) * rvec[2], R_z)
    matrices.append(R_y.tolist())
    # OpenMVG work with the camera center and not with translation directly
    c_x = -np.dot(R_x, tvec)[0]
    center.append(c_x)
    c_y = -np.dot(R_y, tvec)[1]
    center.append(c_y)
    c_z = -np.dot(R_z, tvec)[2]
    center.append(c_z)

    # Index to obtain the ID.
    try:
        match = filenames.index(feats[i])
    except:
        match = 'None'
        print('No view ID was in the sfm_data file which matched the feat')

    if type(match) == int:
        file_id = ids[match]


    pose["key"] = file_id
    pose["value"]["rotation"] = matrices.copy()
    pose["value"]["center"] = center.copy()
    sfm_data["extrinsics"].append(pose.copy())

with open(f'{main_path}/sfm_data_poses.json', 'w') as p:
    json.dump(sfm_data, p, indent=4)
p.close