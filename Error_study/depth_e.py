#######################
#  Created on: May 22, 2024
#  Author: Adriana GV
#######################

# Libraries
import numpy as np
import json
import yaml
import os
import math
from tqdm import tqdm
import cv2
# import pyzed.sl as sl
import statistics
import analysis_tools as aly
import visual_tools as vis

with open('./config_file_copy.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Parameters & directories
camera = config["camera"]
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
depth_frames = f'{scene}/{config["depth_frames_folder"]}'
colour_frames = f'{scene}/{config["frames_folder"]}'
output_path = f'{scene}/{config["out_path"]}'
# App paths
reprojection_path = f'{output_path}/{config["reprojection_path"]}'
savepath = f'{output_path}/{config["depth_path"]}'
save_outliers = f'{output_path}/{config["depth_path"]}/outliers'
save_for_regress = f'{main_path}/{config["calibration_path"]}'
os.makedirs(savepath, exist_ok=True)
# os.makedirs(save_outliers, exist_ok=True)
os.makedirs(save_for_regress, exist_ok=True)
# App files
svo_file = f'{scene}/{config["svo_file"]}'
reprojection_sfm = f'{reprojection_path}/{config["reprojection_file_checker"]}'
savefile = f'{savepath}/{config["depth_file"]}'

with open(reprojection_sfm, 'r') as recosntruction:
    sfm_data = json.load(recosntruction)
recosntruction.close

filenames = []
keys = []
for view in sfm_data["views"]:
    filename = view["value"]["ptr_wrapper"]["data"]["filename"]
    filenames.append(filename)
    key = view["value"]["ptr_wrapper"]["data"]["id_view"]
    keys.append(key)


camera_depth, mvg_depth, depths_error, ratios = [], [], [], []
nan_value = 0
print(f'Running depth study for {len(sfm_data["structure"])} points')
for point in tqdm(sfm_data["structure"]):
    pos = 0
    if len(point["value"]["observations"]) < 10:
        continue
    else:
        for feat in tqdm(point["value"]["observations"]):
            # Associanted frame
            try:
                match = keys.index(feat["key"])
            except:
                match = 'None'
                
            if type(match) == int:
                # Camera pose
                for pose in sfm_data["extrinsics"]:
                    if feat["key"] == pose["key"]:
                        R = np.array(pose["value"]["rotation"])
                        c = np.array(pose["value"]["center"])
                        # Load depth map
                        name_frame = filenames[match]
                        num_format = name_frame.split('.')
                        only_num = num_format[0].split('left')
                        if len(only_num) == 1:
                            continue
                        depth_frame_name = f'depth_{only_num[1]}.npy'
                        depthmap = np.load(f'{depth_frames}/{depth_frame_name}')
                        # Is camera value valid?
                        coord_x = round(feat["value"]["x"][0])
                        coord_y = round(feat["value"]["x"][1])
                        zed_depth = depthmap.T[coord_x, coord_y]
                        if math.isnan(zed_depth) or math.isinf(zed_depth) or zed_depth > 6500:
                            nan_value += 1
                        else:
                            # Translation vector and Extrinsic Matrix
                            # 3D point coordinates
                            cloud_point = np.array(point["value"]["X"])
                            translated_point = cloud_point - c
                            # Reprojection Equations
                            point_in_pose = np.dot(R, translated_point)
                            mvg_dvalue = point_in_pose[2]
                            depth_error = zed_depth - mvg_dvalue
                            ratio = mvg_dvalue / zed_depth
                            camera_depth.append(zed_depth)
                            mvg_depth.append(mvg_dvalue)
                            depths_error.append(depth_error)
                            point["value"]["observations"][pos]["depth study"] = {
                                "OpenMVG depth": float(mvg_dvalue),
                                "ZED depth": float(zed_depth),
                                "difference": float(depth_error)
                            }
                        pos += 1
                    else:
                        continue
            else:
                pos += 1
                continue

# zed.close()


# # Outliers
clean_cam, clean_mvg, clean_diff = [], [], []
mean_diff, sdt_diff = aly.mae_study(depths_error)
num_outliers = 0
for i in range(len(camera_depth)):
    if abs(depths_error [i]) > (abs(mean_diff) + 3*abs(sdt_diff)):
    # if  abs(depths_error [i]) > 500000:
        # chess_board_image = cv2.imread(f'{colour_frames}/{name_frame}')
        # image = cv2.circle(chess_board_image, (coord_x, coord_y), 3, color=(255, 0, 128), thickness=-1)
        # cv2.imwrite(f'{save_outliers}/{name_frame}_mvg{mvg_dvalue}_{camera}{camera_depth[i]}.png', image)
        num_outliers += 1
        continue
    else:
        clean_cam.append(camera_depth[i])
        clean_mvg.append(mvg_depth[i])
        clean_diff.append(depths_error[i])

# Data save for post-processing
np.save(f'{save_for_regress}/{config["scene"]}_{camera}.npy', np.array(clean_cam))
np.save(f'{save_for_regress}/{config["scene"]}_mvgs.npy', np.array(clean_mvg))

# Ratios
r_cam_mvg_clean = aly.ratios(clean_cam, clean_mvg)

# Statistics
# Camera
cam_mae, cam_std = aly.mae_study(camera_depth)
clean_cam_mae, clean_cam_std = aly.mae_study(clean_cam)
# Ground Truth
gt_mae, gt_std = aly.mae_study(mvg_depth)
clean_gt_mae, clean_gt_std = aly.mae_study(clean_mvg)
#RMSE
rmse = aly.rmse_study(mvg_depth, camera_depth)
clean_rmse = aly.rmse_study(clean_mvg, clean_cam)
# Error
err_mae, err_std = aly.mae_study(depths_error)
clean_err_mae, clean_err_std = aly.mae_study(clean_diff)
# Ratio
ratio_mae, ratio_std = aly.mae_study(r_cam_mvg_clean)
# Error Relativo (Accuracy)
re_avg, re_std = aly.re_acc(camera_depth, mvg_depth)
clean_re_avg, clean_re_avg = aly.re_acc(clean_cam, clean_mvg)

# Save data in JSON file
sfm_data["Depth study statistics"] = {
    "Raw data": {
        "Mean error (mm)": float(err_mae),
        "Depth error std (mm)": float(err_std),
        "Mean camera's accuracy respect to OpenmVG": float(re_avg),
        "std camera's accuracy respect to OpenmVG": float(re_std),
        "Root Mean Square Error": float(rmse),
        "Max depth error (mm)": float(max(depths_error)),
        "Min depth error (mm)": float(min(depths_error))
    },
    "Clean data": {
        "Mean error (mm)": float(clean_err_mae),
        "Depth error std (mm)": float(clean_err_std),
        "Mean camera's accuracy respect to OpenmVG": float(clean_re_avg),
        "std camera's accuracy respect to OpenmVG": float(clean_re_avg),
        "Root Mean Square Error": float(clean_rmse),
        "Max depth error (mm)": float(max(clean_diff)),
        "Min depth error (mm)": float(min(clean_diff))
    },
    "Total 3D points given by OpenMVG": len(sfm_data["structure"]),
    "Camera NaN values": nan_value,
    "Removed outliers": num_outliers
}

print(f'Saving results in {savepath}')
with open(savefile, 'w') as dpth:
    json.dump(sfm_data, dpth, indent=4)
dpth.close


# Charts
# Histograms per data
# Camera
vis.hist_chart(clean_cam, f'{camera} depth values', 'Depth values (mm)', 'Nº of points', f'{savepath}/{camera}_histogram')
# # OpenMVG
vis.hist_chart(clean_mvg, 'OpenMVG depth values', 'Depth values (mm)', 'Nº of points', f'{savepath}/OpenMVG_histogram')
# # Diff depths
vis.hist_chart(clean_diff, f'Difference in depth between OpenMVG & {camera} values', 'Depth values (mm)', 'Nº of points', f'{savepath}/diffs_clean_histogram')

# Joint charts
# Camera - OpenMVG
# Double Histogram
vis.double_hist_chart(clean_cam, clean_mvg, f'{camera} & OpenMVG depth values', 'Depth values (mm)', 'Nº of points', f'{camera}', 'OpenMVG', f'{savepath}/{camera}_OpenMVG_histogram')
# Double Boxplot
vis.double_boxplot(clean_cam, clean_mvg, f'{camera} & OpenMVG Boxplot', 'Depth source', 'Depth values (mm)', f'{camera}', 'OpenMVG', f'{savepath}/{camera}_OpenMVG_boxplot')
# KDE plot with distibution in axes
vis.double_kde(clean_cam, clean_mvg, f'{camera} & OpenMVG density plot', 'Depth values (mm)', 'Density', f'{camera}', 'OpenMVG',  f'{savepath}/{camera}_OpenMVG_kde')
# Linear regression
vis.reg(clean_cam, clean_mvg, f'{camera} & OpenMVG linear regression plot', f'{camera}', 'OpenMVG', f'{camera} depth values (mm)', 'OpenMVG depth values (mm)', f'{savepath}/{camera}_OpenMVG_regress')

# Error
vis.scat(clean_cam, clean_diff, f'{camera} & OpenMVG depth values',  f'{camera}', f'Error', 'Depth values (mm)', 'Error with OpenMVG as GT (mm)', f'{savepath}/diff_scatter_clean')

# Ratio
vis.scat(clean_cam, r_cam_mvg_clean, f'Ratio vs. {camera} depth',  f'{camera}', 'Ratio', 'Depth values (mm)', f'Ratio OpenMVG/{camera}', f'{savepath}/ratio_clean_scatter')
