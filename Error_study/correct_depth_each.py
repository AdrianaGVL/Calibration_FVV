#######################
#  Created on: May 22, 2024
#  Author: Adriana GV
#######################

# Libraries
import sys
sys.path.append(os.getcwd())
import numpy as np
import json
import yaml
import os
import numpy as np
import math
import copy
import pandas as pd
from tqdm import tqdm
from scipy import stats
import cv2
import statistics
from utils_py import analysis_tools as aly
from utils_py import visual_tools as vis
from sklearn.linear_model import LinearRegression

config_f =  sys.argv[1]
with open(config_f, 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Parameters & directories
camera = config["camera"]
serial_num = config["serial_num"]
main_path = config["working_path"]
calib_path = f'{main_path}/{config["calibration_path"]}'
regress_params = f'{calib_path}/{config["err_params_file"]}'

# Results structure
results = {
    'Scenes':{
        'Corrective scene': '',
        'Regression function': {},
        'Corrected scenes': []
    }
}

with open(regress_params, 'r') as params:
    r = yaml.safe_load(params)
params.close

scenes, depths, mvgs, errs, ratios = [], [], [], [], []
for directory in os.listdir(f'{main_path}'):
    if os.path.isdir(f'{main_path}/{directory}') and directory != f'{config["calibration_path"]}':
        scenes.append(directory)
for scene in scenes:
    depth = np.load(f'{calib_path}/{scene}_{camera}.npy')
    depths.append(depth)
    mvg = np.load(f'{calib_path}/{scene}_mvgs.npy')
    mvgs.append(mvg)
    err = depth - mvg
    errs.append(err)

# Quadratic
for j in range(len(scenes)):
    # Results structure
    results = {
        'Scenes':{
            'Corrective scene': '',
            'Regression function': {},
            'Corrected scenes': []
        }
    }
    results['Scenes']['Corrective scene'] = scenes[j]
    results['Scenes']['Regression function'] = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Quadratic regression']
    a = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Quadratic regression']['a']
    b = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Quadratic regression']['b']
    c = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Quadratic regression']['offset']
    for s in range(len(r['Parameterisation study per scene'])):
        corrected_scenes = {
            'Name': '',
            'Mean error without correction': '',
            'Std without correction': '',
            'Mean error': '',
            'Std': '',
            'Max. error': '',
            'Min. error': '',
            'New coefficients': ''
        }
        corrected_depth, corrected_ratio = [], []
        if s != j:
            for l in range(len(depths[s])):
                corrected_scenes['Name'] = scenes[s]
                new_depth = a*(depths[s][l]**2) + b*depths[s][l] + c
                new_ratio = mvgs[s][l] / new_depth
                corrected_ratio.append(new_ratio)
                corrected_depth.append(new_depth)

            # Error in depth
            new_err = corrected_depth - mvgs[s]

            # Statistic
            corrected_scenes['Mean error without correction'], corrected_scenes['Std without correction'] = aly.mae_study(errs[s])
            corrected_scenes['Mean error'], corrected_scenes['Std'] = aly.mae_study(new_err)
            corrected_scenes['Max. error'] = max(new_err)
            corrected_scenes['Min. error'] = min(new_err)

            # Linear regresion
            model = LinearRegression()
            model.fit(np.array(corrected_depth).reshape(-1, 1), np.array(new_err).reshape(-1, 1))
            slope =  model.coef_
            intercept = model.intercept_
            corrected_scenes['New coefficients'] = f'Slope = {slope} - Offset = {intercept}'

            vis.scat_con_trend(corrected_depth, corrected_ratio, f'Ratio vs. {camera} depth',  f'{camera}', 'Ratio', 'Depth values (mm)', f'Ratio OpenMVG/{camera}', f'{calib_path}/ratio_qua_scatter_{scenes[j]}_{scenes[s]}')

            corrected_depth.clear()
            corrected_ratio.clear()

            results['Scenes']['Corrected scenes'].append(copy.deepcopy(corrected_scenes))
            
    with open(f'{calib_path}/{scenes[j]}_qua_correction.json', 'w') as corrections:
        json.dump(results, corrections, indent=4)
    corrections.close


# Linear
for j in range(len(scenes)):
    # Results structure
    results = {
        'Scenes':{
            'Corrective scene': '',
            'Regression function': {},
            'Corrected scenes': []
        }
    }
    results['Scenes']['Corrective scene'] = scenes[j]
    results['Scenes']['Regression function'] = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Linear regression']
    a = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Linear regression']['a']
    c = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Linear regression']['offset']
    for s in range(len(r['Parameterisation study per scene'])):
        corrected_scenes = {
            'Name': '',
            'Mean error without correction': '',
            'Std without correction': '',
            'Mean error': '',
            'Std': '',
            'Max. error': '',
            'Min. error': '',
            'New coefficients': ''
        }
        corrected_depth, corrected_ratio = [], []
        if s != j:
            for l in range(len(depths[s])):
                corrected_scenes['Name'] = scenes[s]
                new_depth = a*depths[s][l] + c
                new_ratio = mvgs[s][l] / new_depth
                corrected_ratio.append(new_ratio)
                corrected_depth.append(new_depth)

            # Error in depth
            new_err = corrected_depth - mvgs[s]

            # Linear regresion
            model = LinearRegression()
            model.fit(np.array(corrected_depth).reshape(-1, 1), np.array(new_err).reshape(-1, 1))
            slope =  model.coef_
            intercept = model.intercept_
            corrected_scenes['New coefficients'] = f'Slope = {slope} - Offset = {intercept}'

            # Statistic
            corrected_scenes['Mean error without correction'], corrected_scenes['Std without correction'] = aly.mae_study(errs[s])
            corrected_scenes['Mean error'], corrected_scenes['Std'] = aly.mae_study(new_err)
            corrected_scenes['Max. error'] = max(new_err)
            corrected_scenes['Min. error'] = min(new_err)

            vis.scat_con_trend(corrected_depth, corrected_ratio, f'Ratio vs. {camera} depth',  f'{camera}', 'Ratio', 'Depth values (mm)', f'Ratio OpenMVG/{camera}', f'{calib_path}/ratio_lin_scatter_{scenes[j]}_{scenes[s]}')

            corrected_depth.clear()
            corrected_ratio.clear()

            results['Scenes']['Corrected scenes'].append(copy.deepcopy(corrected_scenes))
            
    with open(f'{calib_path}/{scenes[j]}_lin_correction.json', 'w') as corrections:
        json.dump(results, corrections, indent=4)
    corrections.close


# Cubic
for j in range(len(scenes)):
    # Results structure
    results = {
        'Scenes':{
            'Corrective scene': '',
            'Regression function': {},
            'Corrected scenes': []
        }
    }
    results['Scenes']['Corrective scene'] = scenes[j]
    results['Scenes']['Regression function'] = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Cubic regression']
    a = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Cubic regression']['a']
    b = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Cubic regression']['b']
    c = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Cubic regression']['c']
    d = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Cubic regression']['offset']
    for s in range(len(r['Parameterisation study per scene'])):
        corrected_scenes = {
            'Name': '',
            'Mean error without correction': '',
            'Std without correction': '',
            'Mean error': '',
            'Std': '',
            'Max. error': '',
            'Min. error': '',
            'New coefficients': ''
        }
        corrected_depth = []
        if s != j:
            for l in range(len(depths[s])):
                corrected_scenes['Name'] = scenes[s]
                new_depth = a*(depths[s][l]**3) + b*(depths[s][l]**2) + c*depths[s][l] + d
                new_ratio = mvgs[s][l] / new_depth
                corrected_ratio.append(new_ratio)
                corrected_depth.append(new_depth)

            # Error in depth
            new_err = corrected_depth - mvgs[s]

            # Linear regresion
            model = LinearRegression()
            model.fit(np.array(corrected_depth).reshape(-1, 1), np.array(new_err).reshape(-1, 1))
            slope =  model.coef_
            intercept = model.intercept_
            corrected_scenes['New coefficients'] = f'Slope = {slope} - Offset = {intercept}'

            # Statistic
            corrected_scenes['Mean error without correction'], corrected_scenes['Std without correction'] = aly.mae_study(errs[s])
            corrected_scenes['Mean error'], corrected_scenes['Std'] = aly.mae_study(new_err)
            corrected_scenes['Max. error'] = max(new_err)
            corrected_scenes['Min. error'] = min(new_err)

            vis.scat_con_trend(corrected_depth, corrected_ratio, f'Ratio vs. {camera} depth',  f'{camera}', 'Ratio', 'Depth values (mm)', f'Ratio OpenMVG/{camera}', f'{calib_path}/ratio_cub_scatter_{scenes[j]}_{scenes[s]}')

            corrected_depth.clear()
            corrected_ratio.clear()

            results['Scenes']['Corrected scenes'].append(copy.deepcopy(corrected_scenes))
            
    with open(f'{calib_path}/{scenes[j]}_cub_correction.json', 'w') as corrections:
        json.dump(results, corrections, indent=4)
    corrections.close

# 4º
for j in range(len(scenes)):
    # Results structure
    results = {
        'Scenes':{
            'Corrective scene': '',
            'Regression function': {},
            'Corrected scenes': []
        }
    }
    results['Scenes']['Corrective scene'] = scenes[j]
    results['Scenes']['Regression function'] = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Fourth grade regression']
    a = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Fourth grade regression']['a']
    b = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Fourth grade regression']['b']
    c = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Fourth grade regression']['c']
    d = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Fourth grade regression']['d']
    e = r['Parameterisation study per scene'][j]['Scene']['Regressions']['Fourth grade regression']['offset']
    for s in range(len(r['Parameterisation study per scene'])):
        corrected_scenes = {
            'Name': '',
            'Mean error without correction': '',
            'Std without correction': '',
            'Mean error': '',
            'Std': '',
            'Max. error': '',
            'Min. error': '',
            'New coefficients': ''
        }
        corrected_depth = []
        if s != j:
            for l in range(len(depths[s])):
                corrected_scenes['Name'] = scenes[s]
                new_depth = a*(depths[s][l]**4) + b*(depths[s][l]**3) + c*(depths[s][l]**2) +d*depths[s][l] + e
                new_ratio = mvgs[s][l] / new_depth
                corrected_ratio.append(new_ratio)
                corrected_depth.append(new_depth)

            # Error in depth
            new_err = corrected_depth - mvgs[s]

            # Linear regresion
            model = LinearRegression()
            model.fit(np.array(corrected_depth).reshape(-1, 1), np.array(new_err).reshape(-1, 1))
            slope =  model.coef_
            intercept = model.intercept_
            corrected_scenes['New coefficients'] = f'Slope = {slope} - Offset = {intercept}'

            # Statistic
            corrected_scenes['Mean error without correction'], corrected_scenes['Std without correction'] = aly.mae_study(errs[s])
            corrected_scenes['Mean error'], corrected_scenes['Std'] = aly.mae_study(new_err)
            corrected_scenes['Max. error'] = max(new_err)
            corrected_scenes['Min. error'] = min(new_err)

            vis.scat_con_trend(corrected_depth, corrected_ratio, f'Ratio vs. {camera} depth',  f'{camera}', 'Ratio', 'Depth values (mm)', f'Ratio OpenMVG/{camera}', f'{calib_path}/ratio_fourth_scatter_{scenes[j]}_{scenes[s]}')

            corrected_depth.clear()
            corrected_ratio.clear()

            results['Scenes']['Corrected scenes'].append(copy.deepcopy(corrected_scenes))
            
    with open(f'{calib_path}/{scenes[j]}_fourth_correction.json', 'w') as corrections:
        json.dump(results, corrections, indent=4)
    corrections.close