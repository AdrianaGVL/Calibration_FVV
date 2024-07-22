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
import cv2
import numpy as np
import argparse 
import os

def progress_bar(percent_done, bar_length=50):
    #Display progress bar
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %i%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()

    
def main():
    # Create a InitParameters object and set configuration parameters
    filepath = opt.input_svo_file # Path to the .svo file to be playbacked
    filename = filepath.split('/')[-1].split('.')[0]
    output_path = opt.output_path
    os.makedirs(output_path, exist_ok=True)
    colour_path = output_path +'/colour_frames'
    os.makedirs(colour_path, exist_ok=True)
    depth_path = output_path +'/depth_frames'
    os.makedirs(depth_path, exist_ok=True)
    input_type = sl.InputType()
    input_type.set_from_svo_file(filepath)  #Set init parameter to run from the .svo 
    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False, camera_disable_self_calib=True)
    init.depth_mode = sl.DEPTH_MODE.QUALITY  # New cameras (ZED2) use ULTRA depth mode | Old cameras (Previous firmware) use QUALITY
    init.coordinate_units = sl.UNIT.MILLIMETER  # Use meter units (for depth measurements)
    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS: #Ensure the camera opened succesfully 
        print("Camera Open", status, "Exit program.")
        exit(1)
    
    runtime = sl.RuntimeParameters()
    
    imagel = sl.Mat()
    imager = sl.Mat()
    
    nb_frames = zed.get_svo_number_of_frames()
    print("[Info] SVO contains " ,nb_frames," frames")

    # Obtain claibration parameters
    zed_info = zed.get_camera_information()
    model = ("{0}".format(zed_info.camera_model)).replace(" ", "")
    sn = "{0}".format(zed_info.serial_number)
    print("Extracting frames from camera model ",model," with serial number: ",sn)
    nb_frames = zed.get_svo_number_of_frames()
    fps = zed.get_init_parameters().camera_fps
    print("[Info] SVO contains " ,nb_frames," frames at ",fps)
    resolution = zed_info.camera_resolution
    width = resolution.width
    height = resolution.height
    calibration_params = zed_info.camera_configuration.calibration_parameters_raw

    while True:  # for 'q' key
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            # Images
            svo_position = zed.get_svo_position()
            left_path = colour_path +'/left' + str(svo_position) + '_' + model + '_' + sn + '.png'
            rigth_path = colour_path +'/right' + str(svo_position) + '_' + model + '_' + sn + '.png'
            # Save colour image
            zed.retrieve_image(imagel,sl.VIEW.LEFT,sl.MEM.CPU) #retrieve image left
            zed.retrieve_image(imager,sl.VIEW.RIGHT,sl.MEM.CPU)
            imgl = imagel.write(left_path)
            imgr = imager.write(rigth_path)
            if imgl == sl.ERROR_CODE.SUCCESS:
                print("Saved image : ",left_path)
            else:
                print("Something wrong happened with left image ",svo_position)
            if imgr == sl.ERROR_CODE.SUCCESS:
                print("Saved image : ",rigth_path)
            else:
                print("Something wrong happened with rigth image ",svo_position)

            with open (colour_path + '/lists.txt', 'a') as zi:
                zi.write(f'left{str(svo_position)}{filename}.png;{width};{height};{calibration_params.left_cam.fx};0;{calibration_params.left_cam.cx};0;{calibration_params.left_cam.fy};{calibration_params.left_cam.cy};0;0;1\n')
                zi.write(f'right{str(svo_position)}{filename}.png;{width};{height};{calibration_params.right_cam.fx};0;{calibration_params.right_cam.cx};0;{calibration_params.right_cam.fy};{calibration_params.right_cam.cy};0;0;1\n')
            zi.close
            break
                

        elif err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED: #Check if the .svo has ended
            progress_bar(100, 30) 
            print("SVO end has been reached")
            break
    cv2.destroyAllWindows()
    zed.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_svo_file', type=str, help='Path to the SVO file', required= True)
    parser.add_argument('--output_path', type=str, help='Path where colour images are saved', required= True)
    opt = parser.parse_args()
    if not opt.input_svo_file.endswith(".svo") and not opt.input_svo_file.endswith(".svo2"): 
        print("--input_svo_file parameter should be a .svo file but is not : ",opt.input_svo_file,"Exit program.")
        exit()
    if not os.path.isfile(opt.input_svo_file):
        print("--input_svo_file parameter should be an existing file but is not : ",opt.input_svo_file,"Exit program.")
        exit()
    main()