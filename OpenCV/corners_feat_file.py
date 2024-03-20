#Libraries
import cv2
import glob
import time
import os
from natsort import natsorted
import numpy as np

# Paths
main_path = '/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
scene_path = f'{main_path}/frames'
results_path = f'{main_path}/output'
drawn_corners_path = f'{results_path}/frames_with_corners_opencv_test'

# Save Images with drawn corners?
img_with_corners = False
img_corners_show = False    # Print every image with its drawn corners for 3s (can be change to wait key)

# Number or corners along the x axes and y axes
nCorners_x = 5
nCorners_y = 10

# Coordinates for test?
testing = False
num_samples = 3
if testing:
    features_path = f'{results_path}/Testing_matches'
else:
    features_path = f'{results_path}/matches_for_known'
os.makedirs(features_path, exist_ok=True)

# List the images (frames in this case)
chess_images = natsorted(glob.glob(f'{scene_path}/*.jpeg'))

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
            cv2.drawChessboardCorners(chess_board_image, (1, 1), corners[1], fconers) #(nCorners_x, nCorners_y)
            cv2.imwrite(f'{drawn_corners_path}/IMG_{str(i)}.png', chess_board_image)
            if img_corners_show:
                cv2.imshow(f'{file} with corners',chess_board_image)
                time.sleep(20)   #cv2.waitKey()

        # .feat files are created
        with open(f'{features_path}/{file_file}.feat', 'w') as f:
            if testing:
                i = 0
                while i < num_samples:
                    f.write(f'{corners[i][0][0]} {corners[i][0][1]} 1 0\n')
                    i += 1
            else:
                for coord in corners:
                    f.write(f'{coord[0][0]} {coord[0][1]} 1 0\n')
        f.close

        # .desc files are created
        # data = np.empty(dtype=np.uint8, shape = (desc.size + 8))
        # data[0:8].view(dtype=np.uint64)[0] = desc.shape[0]
        # data[8:] = desc.flatten()

        # with open(path,'wb') as d:
        #     data(f,sep='')
        # d.close