#######################
#  Created on: March 18, 2024
#  Author: Adriana GV
#######################

#Libraries
import sys
import cv2
import glob
import time
import os
from natsort import natsorted
import numpy as np
import yaml

# Config file
config_f =  sys.argv[1]
with open(config_f, 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Paths
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
frames_path = f'{scene}/{config["frames_folder"]}'
drawn_corners_path = f'{output_path}/frames_with_corners'

# Save Images with drawn corners?
img_with_corners = False
img_corners_show = False    # Print every image with its drawn corners for 3s (can be change to wait key)

# Number or corners along the x axes and y axes
nCorners_x = config["num_corners_x"]
nCorners_y = config["num_corners_y"]

# Coordinates for test?
features_path = f'{output_path}/matches_for_known'
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