#######################
#  Created on: June 12, 2024
#  Author: Adriana GV
#######################

# Libraries
import yaml
import json
import glob
import torch
import torch.hub
from tqdm import tqdm
from torchvision import models, transforms
import numpy as np
import matplotlib.pyplot as plt
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


# Download pretrained DeepLabv3
# model = models.segmentation.deeplabv3_resnet101(pretrained=True).eval()

# Pytorch version of DeepLabv2 pre-trained with COCO-Stuff dataset
model = torch.hub.load("kazuto1011/deeplab-pytorch", "deeplabv2_resnet101", pretrained='cocostuff164k', n_classes=182).eval()

# image to tensor
preprocess = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Image Pre-processing
def preprocess_image(image_path):
    input_image = Image.open(image_path).convert("RGB")
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0)  # Crear un lote con una sola imagen
    return input_batch, input_image

# Floor segmentation function
def segment_floor(image_path):
    input_batch, input_image = preprocess_image(image_path)

    # move the input and model to GPU for speed if available
    if torch.cuda.is_available():
        input_batch = input_batch.to('cuda')
        model.to('cuda')

    with torch.no_grad():
        output = model(input_batch.float())
    output_predictions = output.byte().cpu().numpy()
    with open(f'{frames_path}/prueba_numpy.txt', 'a') as p:
            p.write(f'{output_predictions}')
    p.close
    # Class floor labels
    desired_classes = [1,114,115,116,117,118,126,140,145,152]
    # desired_classes = [1]

    # # Floor masks
    # all_floors = ''
    # count = 0
    # for label in output_predictions[0]:
    #     if np.isin(count, desired_classes):
    #         if all_floors == '':
    #             all_floors = label
    #         else:
    #             all_floors += label
    #         count += 1
    #     else:
    #         count += 1
    #         continue
    # # all_floors[all_floors < 0.3] = 0
    # with open(f'{frames_path}/all_masks.txt', 'a') as p:
    #         p.write(f'{all_floors}')
    # p.close
    # # Mask & image to numpy array
    # # all_floors_big = np.array(all_floors.resize(input_image.size))
    # image_np = np.array(input_image.resize(all_floors.shape, Image.NEAREST))
    # floor_np = image_np
    # for channel in range(image_np.shape[2]):
    #     floor_np[:,:,channel]  = image_np[:,:,channel] * all_floors.T

    # # Recover original image but only with the floor
    # floor = Image.fromarray(floor_np
    palette = torch.tensor([2 ** 25 - 1, 2 ** 15 - 1, 2 ** 21 - 1])
    colors = torch.as_tensor([i for i in range(21)])[:, None] * palette
    colors = (colors % 255).numpy().astype("uint8")

    # plot the semantic segmentation predictions of 21 classes in each color
    r = Image.fromarray(output_predictions).resize(input_image.size)
    r.putpalette(colors)
    return r
    

frames = glob.glob(f'{frames_path}/*.jpeg')
for frame in tqdm(frames):
    print(frame)
    frame_name = frame.split('/')[-1]
    floor_image = segment_floor(frame)
    floor_image.save(f'{frames_path}/floor_{frame_name}')