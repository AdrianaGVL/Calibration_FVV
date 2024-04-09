#######################
#  Created on: March 18, 2024
#  Author: Adriana GV
#######################

#Libraries
import cv2
import glob
import time
import os
from natsort import natsorted
import numpy as np

# Paths
main_path = '/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
scene_path = f'{main_path}/Video_Chess_C'
frames_path = f'{scene_path}/frames_I'
results_path = f'{scene_path}/output_chiquito'
drawn_corners_path = f'{results_path}/frames_with_corners'

# Save Images with drawn corners?
img_with_corners = False
img_corners_show = False    # Print every image with its drawn corners for 3s (can be change to wait key)

# Number or corners along the x axes and y axes
nCorners_x = 8
nCorners_y = 6

# Coordinates for test?
features_path = f'{results_path}/matches_for_known'
os.makedirs(features_path, exist_ok=True)

# List the images (frames in this case)
chess_images = natsorted(glob.glob(f'{frames_path}/*.png'))

# Loop to iterate along all the images
for i in range(len(chess_images)):
    # Read in the image
    chess_board_image = cv2.imread(chess_images[i])
    file = os.path.basename(chess_images[i])
    file_file = file.split('.')[0]
    print(f'File: {file}')
    # Convert to grayscale
    gray = cv2.cvtColor(chess_board_image, cv2.COLOR_RGB2GRAY)
    # Find the chessboard corners
    fconers, corners = cv2.findChessboardCorners(gray, (nCorners_x, nCorners_y), cv2.CALIB_CB_EXHAUSTIVE + cv2.CALIB_CB_ACCURACY)

    # If found, draw corners
    if fconers:

        if img_with_corners:
            os.makedirs(drawn_corners_path, exist_ok=True)
            # Draw the corners
            cv2.drawChessboardCorners(chess_board_image, (1, 1), corners[1], fconers) #(nCorners_x, nCorners_y), corners,
            cv2.imwrite(f'{drawn_corners_path}/IMG_{str(i)}.png', chess_board_image)
            if img_corners_show:
                cv2.imshow(f'{file} with corners',chess_board_image)
                time.sleep(20)   #cv2.waitKey()

        # .feat files are created
        with open(f'{features_path}/{file_file}.feat', 'w') as f:
            for coord in corners:
                    f.write(f'{coord[0][0]} {coord[0][1]} 1 0\n')
        f.close

    else:
        with open(f'{features_path}/{file_file}.feat', 'w') as f:
            f.write(f'')
        f.close