#######################
#  Created on: May 9, 2024
#  Author: Adriana GV
#######################

########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

"""
    Read SVO sample to read the video and the information of the camera. It can pick a frame of the svo and save it as
    a JPEG or PNG file. Depth map and Point Cloud can also be saved into files.
"""
import sys
import pyzed.sl as sl
import copy
import numpy as np
import argparse 
import os
import yaml
import json
import shutil

def progress_bar(percent_done, bar_length=50):
    #Display progress bar
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %i%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()

# JSON structure
zed_depth = {
    "ZED Model": '',
    "ZED Serial Number": '',
    "Recording fps": '',
    "root_path": '',
    "intrinsic": []
}

intrisics = {
    "width": '',
    "height": '',
    "focal length left camera": [],
    "principal_point": [],
    "disto_k3": []
}

    
def main():
    # Create a InitParameters object and set configuration parameters
    svo_path = opt.input_svo_file # Path to the .svo file to be playbacked
    config_path = opt.input_config_file
    init_params = sl.InitParameters()
    run_params = sl.RuntimeParameters()
    init_params.set_from_svo_file(svo_path)
    init_params.depth_mode = sl.DEPTH_MODE.QUALITY 
    init_params.coordinate_units = sl.UNIT.MILLIMETER
    zed = sl.Camera()
    status = zed.open(init_params)
    if status != sl.ERROR_CODE.SUCCESS: #Ensure the camera opened succesfully 
        print("SVO file Open", status, "Exit program.")
        exit(1)
    
    image = sl.Mat()
    depth = sl.Mat()
    
    nb_frames = zed.get_svo_number_of_frames()
    print("[Info] SVO contains " ,nb_frames," frames")
    final_frames = nb_frames
    lim_frames = 1
    while final_frames > 800:
        lim_frames += 1
        final_frames = nb_frames / lim_frames

    # Cam_info
    zed_info = zed.get_camera_information()
    model = ("{0}".format(zed_info.camera_model)).replace(" ", "")
    zed_depth["ZED Model"] = model
    sn = "{0}".format(zed_info.serial_number)
    zed_depth["ZED Serial Number"] = sn

    # New cam path
    split_path = svo_path.split('/')
    filename = (split_path).pop()
    filepath = '/'.join(split_path)
    cam_path = f'{filepath}/{model}_{sn}'
    os.makedirs(cam_path, exist_ok=True)
    scene = (filename.split('.')[0]).replace("-", "_")
    scene_path = f'{cam_path}/{scene}'
    os.makedirs(scene_path, exist_ok=True)
    zed_depth["root_path"] = svo_path
    colour_path = scene_path +'/colour_frames'
    os.makedirs(colour_path, exist_ok=True)
    init_params.save(f"{scene_path}/initParameters.conf") # Export the parameters into a file
    run_params.save(f"{scene_path}/runtParameters.conf")

    # Cam and recording data
    zed_depth["Recording fps"] = zed.get_init_parameters().camera_fps
    resolution = zed_info.camera_resolution
    width = resolution.width
    height = resolution.height
    intrisics["width"] = width
    intrisics["height"] = height
    # Obtain calibration parameters
    calibration_params = zed_info.camera_configuration.calibration_parameters_raw
    print(calibration_params)
    intrisics["principal_point"].append(calibration_params.left_cam.cx)
    intrisics["principal_point"].append(calibration_params.left_cam.cy)
    intrisics["focal length left camera"].append(calibration_params.left_cam.fx)
    intrisics["focal length left camera"].append(calibration_params.left_cam.fy)
    dist = calibration_params.left_cam.disto
    for value in dist:
        intrisics["disto_k3"].append(value)
    zed_depth["intrinsic"].append(copy.deepcopy(intrisics))

    with open (f'{scene_path}/svo_info.json', 'w') as zi:
        json.dump(zed_depth, zi, indent=4)
    zi.close

    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    config_file.close

    with open(config_path, 'w') as config_file:
        config["camera"] = model
        config["serial_num"] = sn
        config["svo_file"] = filename
        config["calibration"] = 'svo_info.json'
        config["scene"] = scene
        yaml.dump(config, config_file, indent=4, default_style=None, default_flow_style=False) # sort_keys=False
    config_file.close

    count = 0
    while True:  # for 'q' key
        err = zed.grab()
        if err == sl.ERROR_CODE.SUCCESS:
            if count == (lim_frames-1):
                # Images
                svo_position = zed.get_svo_position()
                left_path = colour_path +'/colour_' + str(svo_position) + '.png'
                # Save colour image
                zed.retrieve_image(image,sl.VIEW.LEFT,sl.MEM.CPU) #retrieve image left
                img = image.write(left_path)
                if img == sl.ERROR_CODE.SUCCESS:
                    print("Saved image : ",left_path)
                else:
                    print("Something wrong happened with image ",svo_position)
                count = 0
            else:
                count += 1
                

        elif err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED: #Check if the .svo has ended
            progress_bar(100, 30) 
            print("SVO end has been reached")
            break
    zed.close()

    shutil.move(svo_path, f'{scene_path}/{filename}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_svo_file', type=str, help='Path to the SVO file', required= True)
    parser.add_argument('--input_config_file', type=str, help='Path to the config file', required= True)
    opt = parser.parse_args()
    if not opt.input_svo_file.endswith(".svo") and not opt.input_svo_file.endswith(".svo2"): 
        print("--input_svo_file parameter should be a .svo file but is not : ",opt.input_svo_file,"Exit program.")
        exit()
    if not os.path.isfile(opt.input_svo_file):
        print("--input_svo_file parameter should be an existing file but is not : ",opt.input_svo_file,"Exit program.")
        exit()
    main()