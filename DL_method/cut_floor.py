#######################
#  Created on: June 12, 2024
#  Author: Adriana GV
#######################

# Libraries
import yaml
import glob
from PIL import Image

# Config file
with open('../config_DL.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Paths
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
frames_path = f'{scene}/{config["frames_folder"]}'

frames = glob.glob(f'{frames_path}/*.jpeg')
for frame in frames:
    frame_name = frame.split('/')[-1]
    image = Image.open(frame)
    width, height = image.size
    img_black = Image.new('RGB', (width, height), (0, 0, 0))
    left = width*(1/3)
    right = left*2
    upper = (height-1) - (height*(1/4))
    lower = (height-1)
    cut_coords = (left, upper, right, lower)
    paste_coords = (int(left), int(upper))
    area_recorte = (cut_coords)  # (left, upper, right, lower)
    cut = image.crop(area_recorte)
    Image.Image.paste(img_black, cut, paste_coords)
    img_black.save(f'{frames_path}/cut_{frame_name}')