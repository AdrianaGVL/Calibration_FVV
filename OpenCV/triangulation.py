#######################
#  Created on: July 4, 2024
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