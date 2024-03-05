import numpy as np
import cv2
import matplotlib.pyplot as plt
import glob
import pandas as pd
import json
import os

# Path
data_path = '/media/agv/JesusGTI/Calibration/iPhone_Recordings/C_chess/frames'
# Number or corners along the x axes
nCorners_x = 8
# Number or corners along the y axes
nCorners_y = 6
# Array where the coordinates of the corners will be saved
corners = 0
fconers = False
# Dataframe where coordinates of each image are saved
coord_corners = pd.DataFrame()
# Window size to process the subpixel analysis
# Half of the side length of the search window. For example, if winSize=Size(5,5) , then a (5∗2+1)×(5∗2+1)=11×11 search window is used.
subWin = (11, 11)
# Path to the images and list it
chess_images = glob.glob(f'{data_path}/*.png')
# Main JSON
ref_points = {
    "Record": 'C_Chess',
    "Camera": 'iPhone XS Max',
    "Corners": []
}

# Loop to iterate alng all the images
#With only one it could be done, but it is better to try with some and estimate any error, if it exists
for i in range(len(chess_images)):
    # Read in the image
    chess_board_image = cv2.imread(chess_images[i])
    file = os.path.basename(chess_images[i])
    print(f'File: {file}')
    # Convert to grayscale
    gray = cv2.cvtColor(chess_board_image, cv2.COLOR_RGB2GRAY)
    # Find the chessboard corners
    fconers, corners = cv2.findChessboardCorners(chess_board_image, (nCorners_x, nCorners_y), cv2.CALIB_CB_EXHAUSTIVE + cv2.CALIB_CB_ACCURACY) # cv2.CALIB_CB_FAST_CHECK
    # If found, draw corners
    if fconers == True:
        # # Draw and display the corners
        # cv2.drawChessboardCorners(chess_board_image, (nCorners_x, nCorners_y), corners, fconers)
        # result_name = f'/media/agv/JesusGTI/Calibration/Images/corners/IMG_{str(i)}.png'
        # cv2.imwrite(result_name, chess_board_image)
        # cv2.imshow('img',chess_board_image)
        # cv2.waitKey()

        # In ordert to maximize the precision of the coordinates a subpixel method is called
        cv2.cornerSubPix(gray, corners, subWin, (-1, -1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1));
        # print(f'The coordinates of each corner are:\n {corners}')

        # Now the coordinates are save into a JSON
        with open(f'{data_path}/output/openCV_coords_acc.json', 'w') as f:
            chess_coords = {
                    'filename': file,
                    'x': []
            }
            for coord in corners:
                chess_coords['x'].append([f'{coord[0][0]}', f'{coord[0][1]}'])
                ref_points['Corners'].append(chess_coords)

            # Now the coordinates are save into a JSON
            json.dump(ref_points, f, indent=4)
        f.close
