##############################
#  Created on: June 12, 2024 #
#  Author: Adriana GV        #
##############################

#Libraries
import yaml
import os
import numpy as np
import pandas as pd
import sys
sys.path.append(os.getcwd())
from utils_py import analysis_tools as aly
from utils_py import visual_tools as vis

config_f =  sys.argv[1]
with open(config_f, 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Parameters & directories
camera = config["camera"]
serial_num = config["serial_num"]
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
# App paths
calib_path = f'{main_path}/{config["calibration_path"]}'
# App files
# savedf = f'{calib_path}/{config["data_df"]}'
savefile = f'{calib_path}/{config["err_params_file"]}'

print_df_info = True

# Data load ?
if os.path.isfile(f'{calib_path}/stats_clean_df_prueba.csv'):
    print(f'DataFrame already exists. Loading df…')
    stats_clean = pd.read_csv(f'{calib_path}/stats_clean_df.csv')
else:
    if os.path.isfile(f'{calib_path}/erros_per_mm.csv'):
        print(f'DataFrame already exists. Loading df..')
        erros_per_mm = pd.read_csv(f'{calib_path}/erros_per_mm.csv')
    else:
        print(f'DataFrame does not exists. Loading data and creating df…')
        scenes, ratios, depths, mvgs, errors, errs_chart = [], [], [], [], [], []
        filtered_depth, filtered_mvg, depths_filt, mvgs_filt, errs_filt_chart = [], [], [], [], []
        for directory in os.listdir(f'{main_path}'):
            if os.path.isdir(f'{main_path}/{directory}') and directory != f'{config["calibration_path"]}':
                scenes.append(directory)
        scenes.append('sala_fvv')
        scenes.append('sala_yo')
        for scene in scenes:
            depth = np.load(f'{calib_path}/{scene}_{camera}.npy')
            mvg = np.load(f'{calib_path}/{scene}_mvgs.npy')
            depths.append(depth)
            mvgs.append(mvg)
            err_chart = depth - mvg
            errs_chart.append(err_chart)
            for t in range(len(depth)):
                filtered_depth.append(depth[t])
                filtered_mvg.append(mvg[t])
            depths_filt.append(np.array(filtered_depth))
            mvgs_filt.append(filtered_mvg)
            err_filt_chart = np.array(filtered_depth) - np.array(filtered_mvg)
            errs_filt_chart.append(err_filt_chart)
            for d in range(len(filtered_depth)):
                error = filtered_depth[d] - filtered_mvg[d]
                errors.append((error, filtered_depth[d], scene))

            filtered_depth.clear()
            filtered_mvg.clear()
        
        # Plot errors all together
        vis.lines(depths, errs_chart, f'Error vs. {camera} depth values for each video', f'{camera} Depth values (mm)', f'Difference {camera}-OpenMVG (mm)',  scenes, f'{calib_path}/all_trendlines', regression='lowess')
        vis.lines(depths_filt, errs_filt_chart, f'Error vs. {camera} depth values for each video', f'{camera} Depth values (mm)', f'Difference {camera}-OpenMVG (mm)',  scenes, f'{calib_path}/all_filt_trendlines', regression='lowess')
        
        # Remove temporal variables
        del filtered_depth, filtered_mvg, mvgs_filt, depths_filt, err_chart, errs_chart, depths, mvgs, depth, mvg, err_filt_chart, errs_filt_chart, error

        # Create a DataFrame
        depths = sorted(set(round(depth) for _, depth, _ in errors))
        error_dict = {depth: [np.nan] * len(errors) for depth in depths}
        scene_list = []  
        for i, (err, depth, scene) in enumerate(errors):
            rounded_depth = round(depth)
            error_dict[rounded_depth][i] = err
            scene_list.append(scene)

    # Statistics
    print(f'Computing some statistics...')
    columns_to_keep = [col for col in depths]
    stats_per_mm = pd.DataFrame(index=['Samples', 'MAE', 'STD', 'RMSE', 'MAX', 'MIN'], columns=columns_to_keep)
    for column in stats_per_mm.columns:
        if column == 'Scene':
            continue
        else: 
            column_values = np.array(error_dict[column])
            not_nans = column_values[~np.isnan(column_values)]
            
            if len(not_nans) < 2:
                continue
            else:
                stats_per_mm.at['Samples', f'{column}'] = int(len(not_nans))
                stats_per_mm.at['MAE', f'{column}'] = aly.mae_study(not_nans)[0]
                stats_per_mm.at['STD', f'{column}'] = aly.mae_study(not_nans)[1]
                stats_per_mm.at['RMSE', f'{column}'] = aly.rmse_single(not_nans)
                stats_per_mm.at['MAX', f'{column}'] = max(not_nans)
                stats_per_mm.at['MIN', f'{column}'] = min(not_nans)

    filtered_depths = stats_per_mm.columns[stats_per_mm.iloc[0] >= 2]
    stats_clean = stats_per_mm[filtered_depths]
    stats_clean.to_csv(f'{calib_path}/stats_clean_df.csv', index=True)
    print(f'DataFrame was saved in: {calib_path}/stats_clean_df.csv')

if print_df_info:
    print(stats_clean.head(n=6))
    print(stats_clean.info())
    print(stats_clean['3000'])