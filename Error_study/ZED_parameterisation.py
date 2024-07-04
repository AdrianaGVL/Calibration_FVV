##############################
#  Created on: June 12, 2024 #
#  Author: Adriana GV        #
##############################

#Libraries
import yaml
import os
import sys
sys.path.append(os.getcwd())
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
# scene = f'{main_path}/{config["scene"]}'
# output_path = f'{scene}/{config["out_path"]}'
# App paths
# depth_path = f'{output_path}/{config["depth_path"]}'
calib_path = f'{main_path}/{config["calibration_path"]}'
os.makedirs(calib_path, exist_ok=True)
# App files
savefile = f'{calib_path}/{config["err_params_file"]}'


# Data load
scenes, ratios, depths, mvgs, errs = [], [], [], [], []
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

# Values
depths_n, mvgs_n, errors, ratios = [], [], [], []
for f in range(len(depths)):
    for i in range(len(depths[f])):
        depths_n.append(depths[f][i])
        mvgs_n.append(mvgs[f][i])
        errors.append(depths[f][i] - mvgs[f][i])
depths_np = np.array(depths_n)
mvgs_np = np.array(mvgs_n)

# Linear regresion
model = LinearRegression()
model.fit(mvgs_np.reshape(-1, 1), depths_np.reshape(-1, 1))
slope =  model.coef_
intercept = model.intercept_

# Quadratic regression
coeffs2 = np.polyfit(depths_np, mvgs_np, 2)
print(f'Quadratic equation for error correction is: {coeffs2[0]:.3e}x^2 + {coeffs2[1]:.3e}x + {coeffs2[2]:.3e}')

# Tridr grade regression
coeffs3 = np.polyfit(depths_np, mvgs_np, 3)
print(f'Quadratic equation for error correction is: {coeffs3[0]:.3e}x^3 + {coeffs3[1]:.3e}x^2 + {coeffs3[2]:.3e}x + {coeffs3[3]:.3e}')

correction_parameters = {
    'Linear regression':{
        'a': float(slope),
        'offset': float(intercept)
    },
    'Quadratic regression':{
        'a': float(coeffs2[0]),
        'b': float(coeffs2[1]),
        'offset': float(coeffs2[2])
    },
    'Third grade regression':{
        'a': float(coeffs3[0]),
        'b': float(coeffs3[1]),
        'c': float(coeffs3[2]),
        'offset': float(coeffs3[3])
    }
}

print(f'Saving results in {savefile}')
with open(savefile, 'w') as coeff:
    yaml.dump(correction_parameters, coeff, indent=4)
coeff.close

# # Corrected Results
# corrected_depths, new_diffs = [], []
# corrected_depth = []
# for j in range(len(depths)):
#     for k in range(len(depths[j])):
#         v = depths[j][k]
#         new_depth = (coeffs[0]*(v**2) + coeffs[1]*v + coeffs[2])
#         corrected_depth.append(new_depth)
#     corrected_depths.append(corrected_depth.copy())


#     # Plot new values
#     new_diff = []
#     for l in range(len(depths[j])):
#         new_diff.append(corrected_depth[l] - mvgs[j][l])
#     ratio = aly.ratios(corrected_depth, mvgs[j])
#     new_diffs.append(new_diff.copy())

#     vis.scat(corrected_depth, mvgs[j], f'OpenMVG vs. Corrected depth values',  f'{camera}', 'OpenMVG', f'{camera} Corrected Depth values (mm)', f'OpenMVG', f'{calib_path}/{scenes[j]}_corrected_openmvg_scatter')
#     vis.scat(corrected_depth, new_diff, f'Error vs. Corrected depth values',  f'{camera}', 'Diference', f'{camera} Corrected Depth values (mm)', f'Difference {camera}-OpenMVG', f'{calib_path}/{scenes[j]}_corrected_diff_scatter')
#     vis.scat(corrected_depth, ratio, f'Ratio vs. Corrected depth values',  f'{camera}', 'OpenMVG', f'{camera} Corrected Depth values (mm)', f'Ratio OpenMVG/{camera}', f'{calib_path}/{scenes[j]}_corrected_ratio_scatter')

#     corrected_depth.clear()
#     new_diff.clear()

# # lines plot
# vis.lines(corrected_depths, new_diffs, f'Error vs. Corrected {camera} depth values for each video', f' Corrected {camera} Depth values (mm)', f'Difference regressed {camera}-OpenMVG (mm)',  scenes, f'{calib_path}/all_trendlines_corrected', regression='lowess')