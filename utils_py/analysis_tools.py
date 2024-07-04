#!/usr/bin/env python

#######################
#  Created on: June 9, 2024
#  Author: Adriana GV
#######################

# Libraries
import numpy as np
import math
from scipy.stats import pearsonr, zscore
from sklearn.metrics import mean_squared_error

# Euclidean distance
def eu_dis(point1, point2):
    p1 = np.array(point1)
    p2 = np.array(point2)
    distance = np.linalg.norm(p1-p2)
    return distance

# def angles(vector1, vector2):
#     angle = np.arctan2(vector1, vector2)
#     angle_de = (angle * 180) / np.pi
#     return angle_de[0]

# Pearson Analysis
def pearson_study(dataset1, dataset2):
    coef_corr, p_value = pearsonr(dataset1, dataset2)
    return coef_corr, p_value

# Outliers
# Z-Score -> Similar to Pearson
def z_score(data, threshold):
    data_np = np.array(data)
    z = np.abs(zscore(data_np))
    filtered_data = data_np[z < threshold]
    indices_outside_range = np.where(z > (threshold))[0]
    return filtered_data, indices_outside_range

# IQR scores
def iqr_scores(data, factor, lower_bound, upper_bound):
    data_np = np.array(data)
    Q1 = np.quantile(data_np, lower_bound)
    Q3 = np.quantile(data_np, upper_bound)
    IQR = Q3 - Q1
    factorise_iqr = IQR * factor
    filtered_data = data_np[(data_np >= (Q1 - factorise_iqr)) & (data_np <= (Q3 + factorise_iqr))]
    indices_outside_range = np.where((data_np < (Q1 - factorise_iqr)) | (data_np > (Q3 + factorise_iqr)))[0]
    return filtered_data, indices_outside_range

# Error distribution
# MAE -> Distribution analysis without taking into account sign
def mae_study(data):
    abs_values = np.abs(np.array(data))
    avg = np.mean(abs_values)
    std = np.std(abs_values)
    return avg, std

#RSE

# RMSE -> Distribution analysis taking into account sign
def rmse_study(gt, pred):
    gt_np = np.array(gt)
    pred_np = np.array(pred)
    rmse_result = mean_squared_error(gt_np, pred_np)
    return rmse_result

def rmse_single(errs):
    errs_np = np.array(errs)
    rmse_re = np.sqrt(np.mean((errs_np)**2))
    return rmse_re

# Relative Error in Accuracy -> Error depending on a ground truth
def re_acc(measure, gt):
    measure_np = np.array(measure)
    gt_np = np.array(gt)
    re = np.divide(measure_np, gt_np)*100
    avg_re = np.mean(re)
    std_re = np.std(re)
    return avg_re, std_re

def ratios(data1, data2):
    data1_np = np.array(data1)
    data2_np = np.array(data2)
    ratio = np.divide(data2_np, data1_np)
    return ratio