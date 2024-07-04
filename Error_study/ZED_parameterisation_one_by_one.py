##############################
#  Created on: June 12, 2024 #
#  Author: Adriana GV        #
##############################

#Libraries
import sys
sys.path.append(os.getcwd())
import yaml
import os
import numpy as np
import pandas as pd
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
# App paths
calib_path = f'{main_path}/{config["calibration_path"]}'
os.makedirs(calib_path, exist_ok=True)
# App files
savefile = f'{calib_path}/{config["err_params_file"]}'

# Data structure
all_scene_param = {
        'Parameterisation study per scene': []
    }

# Data load
scenes, ratios, depths, mvgs, errs = [], [], [], [], []
for directory in os.listdir(f'{main_path}'):
    if os.path.isdir(f'{main_path}/{directory}') and directory != f'{config["calibration_path"]}':
        scenes.append(directory)
for scene in scenes:
    depths_np = np.load(f'{calib_path}/{scene}_{camera}.npy')
    mvgs_np = np.load(f'{calib_path}/{scene}_mvgs.npy')
    err = depths_np - mvgs_np
    # Error regress
    model_e = LinearRegression()
    model_e.fit(depths_np.reshape(-1, 1), err.reshape(-1, 1))
    slope_e =  model_e.coef_
    intercept_e = model_e.intercept_

    # Linear regresion
    model = LinearRegression()
    model.fit(mvgs_np.reshape(-1, 1), depths_np.reshape(-1, 1))
    slope =  model.coef_
    intercept = model_e.intercept_

    # Quadratic regression
    coeffs2 = np.polyfit(depths_np, mvgs_np, 2)

    # Cubic regression
    coeffs3 = np.polyfit(depths_np, mvgs_np, 3)

    # Fourth grade regression
    coeffs4 = np.polyfit(depths_np, mvgs_np, 4)

    correction_parameters = {
        'Scene':{
            'Name': scene,
            'Error linear function': f'Slope = {slope_e} - Offset = {intercept_e}',
            'Regressions':{
                'Linear regression':{
                    'a': float(slope),
                    'offset': float(intercept)
                },
                'Quadratic regression':{
                    'a': float(coeffs2[0]),
                    'b': float(coeffs2[1]),
                    'offset': float(coeffs2[2])
                },
                'Cubic regression':{
                    'a': float(coeffs3[0]),
                    'b': float(coeffs3[1]),
                    'c': float(coeffs3[2]),
                    'offset': float(coeffs3[3])
                },
                'Fourth grade regression':{
                    'a': float(coeffs4[0]),
                    'b': float(coeffs4[1]),
                    'c': float(coeffs4[2]),
                    'd': float(coeffs4[3]),
                    'offset': float(coeffs4[4])
                }
            }
        }
    }

    all_scene_param['Parameterisation study per scene'].append(correction_parameters)

print(f'Saving results in {savefile}')
with open(savefile, 'w') as coeff:
    yaml.dump(all_scene_param, coeff, indent=4)
coeff.close