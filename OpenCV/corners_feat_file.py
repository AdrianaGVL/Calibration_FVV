#Libraries
import cv2
import glob
import time
import os
import numpy as np
from natsort import natsorted

# Paths
main_path = '/media/agv/JesusGTI/Calibration'
scene_path = f'{main_path}/iPhone_Recordings/C_chess/frames'
drawn_corners_path = f'{scene_path}/output/frames_with_corners_opencv'
features_path = f'{scene_path}/output/matches_for_known'

# Save Images with drawn corners?
img_with_corners = False
img_corners_show = False    # Print every image with its drawn corners for 3s (can be change to wait key)

# Number or corners along the x axes and y axes
nCorners_x = 8
nCorners_y = 6

# Window size to process the subpixel analysis
# Half of the side length of the search window. For example, if winSize=Size(5,5) , then a (5∗2+1)×(5∗2+1)=11×11 search window is used.
subWin = (11, 11)

# # List with all the features and all the descriptors for Exhaustive matching
# all_feats = []
# all_desc = []
# images = []

# List the images (frames in this case)
chess_images = natsorted(glob.glob(f'{scene_path}/*.png'))

# Loop to iterate alng all the images
for i in range(len(chess_images)):
    # Read in the image
    chess_board_image = cv2.imread(chess_images[i])
    file = os.path.basename(chess_images[i])
    file_file = file.split('.')[0]
    print(f'File: {file}')
    # Convert to grayscale
    gray = cv2.cvtColor(chess_board_image, cv2.COLOR_RGB2GRAY)
    # images.append(gray)
    # Find the chessboard corners
    fconers, corners = cv2.findChessboardCorners(gray, (nCorners_x, nCorners_y), cv2.CALIB_CB_EXHAUSTIVE + cv2.CALIB_CB_ACCURACY)

    # If found, draw corners
    if fconers:
        # New image with only the corners
        mask = np.zeros(gray.shape, dtype=np.uint8)
        # print(mask.shape)
        # for coord in corners:
        #     cv2.circle(mask, (int(coord[0][0]), int(coord[0][1])), radius=0, color=(25, 255, 255), thickness=-1)
        #     print(int(coord[0][0]), int(coord[0][1]))
        # cv2.imwrite(f'{drawn_corners_path}/IMG_{str(i)}.png', mask)


        # Draw the corners
        # cv2.drawChessboardCorners(mask, (nCorners_x, nCorners_y), corners, False)

        if img_with_corners:
            cv2.imwrite(f'{drawn_corners_path}/IMG_{str(i)}.png', mask)
            if img_corners_show:
                cv2.imshow(f'{file} with corners',chess_board_image)
                time.sleep(20)   #cv2.waitKey()

        # Convert corners into keypoints
        kp = []
        for coord in corners:
            corner = cv2.KeyPoint(coord[0][0], coord[0][1], 1)
            kp.append(corner)
        keypoints = tuple(kp)
                
        # Create SIFT obj
        sift = cv2.SIFT_create()
        # keypoints, descriptors = sift.detectAndCompute(gray, mask)
        kps, descriptors = sift.compute(gray, keypoints)
        # for kp in kps:
        #     print(kp.size, kp.angle)

        # all_feats.append(kps)
        # all_desc.append(descriptors)

        # .feat and .desc files are created
        with open(f'{features_path}/{file_file}.feat', 'w') as f:
            for kp in keypoints:
                f.write(f'{kp.pt[0]} {kp.pt[1]}\n')
        f.close

        with open(f'{features_path}/{file_file}.desc', 'w') as f:
            for desc in descriptors:
                f.write(f'{desc}\n')

        
# # BFMatcher with default params
# # bf = cv2.BFMatcher()
# matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
# for i in range(len(all_desc)):
#     for j in range(i+1, len(all_desc)):
#         # matches = bf.match(all_desc[i],all_desc[j])
#         matches = matcher.match(all_desc[i],all_desc[j])
#         # # Apply ratio test
#         # good = []
#         # for m,n in matches:
#         #     if m.distance < 0.75*n.distance:
#         #         good.append([m])
#         #         print(m)
#         #         print("Distancia del match:", m.distance)
#         #         print("Índice del descriptor en la primera imagen:", m.queryIdx)
#         #         print("Índice del descriptor en la segunda imagen:", m.trainIdx)
#         #         print("\n\n")

#         img3 = cv2.drawMatches(images[i],all_feats[i],images[j],all_feats[j],matches,None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
#         cv2.imwrite(f'{drawn_corners_path}/IMG_{str(i)}.png', img3)


