#######################
#  Script for extracting files from an SVO file
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
import math
import cv2
import argparse 
import os 

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
    "root_path": '',
    "intrinsic": [],
    "structure": []
}

intrisics = {
    "width": '',
    "height": '',
    "focal length left camera": [],
    "principal_point": [],
    "disto_k3": []
}

point_cloud_points = {
    "key": '',
    "coordinates": []
}

    
def main():
    # Obtain claibration parameters
    zed_info = zed.get_camera_information()
    zed_depth["ZED Model"] = "{0}".format(zed_info.camera_model)
    zed_depth["ZED Serial Number"] = "{0}".format(zed_info.serial_number)
    intrisics["width"] = zed_info.camera_configuration.resolution.width
    intrisics["height"] = zed_info.camera_configuration.resolution.height
    calibration_params = zed_info.camera_configuration.calibration_parameters
    intrisics["principal_point"].append(calibration_params.left_cam.cx)
    intrisics["principal_point"].append(calibration_params.left_cam.cy)
    intrisics["focal length left camera"].append(calibration_params.left_cam.fx)
    intrisics["focal length left camera"].append(calibration_params.left_cam.fy)
    intrisics["disto_k3"] = calibration_params.left_cam.disto
    zed_depth["intrinsic"].append(copy.deepcopy(intrisics))

    # Create a InitParameters object and set configuration parameters
    filepath = opt.input_svo_file # Path to the .svo file to be playbacked
    zed_depth["root_path"] = filepath
    output_path = opt.output_path
    os.makedirs(output_path, exist_ok=True)
    colour_path = f'{output_path}/colour_frames'
    os.makedirs(colour_path, exist_ok=True)
    depth_path = f'{output_path}/depth_frames'
    os.makedirs(depth_path, exist_ok=True)
    input_type = sl.InputType()
    input_type.set_from_svo_file(filepath)  #Set init parameter to run from the .svo 
    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    init.depth_mode = sl.DEPTH_MODE.ULTRA  # Use ULTRA depth mode
    init.coordinate_units = sl.UNIT.MILLIMETER  # Use meter units (for depth measurements)
    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS: #Ensure the camera opened succesfully 
        print("Camera Open", status, "Exit program.")
        exit(1)

    # Set a maximum resolution, for visualisation confort 
    resolution = zed.get_camera_information().camera_configuration.resolution
    
    runtime = sl.RuntimeParameters()
    
    image = sl.Mat()
    depth = sl.Mat()
    # point_cloud = sl.Mat()

    svo_frame_rate = zed.get_init_parameters().camera_fps
    nb_frames = zed.get_svo_number_of_frames()
    print("[Info] SVO contains " ,nb_frames," frames")
    
    while True:  # for 'q' key
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            # Images
            zed.retrieve_image(image,sl.VIEW.LEFT,sl.MEM.CPU) #retrieve image left
            zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
            svo_position = zed.get_svo_position()
            cv2.imshow("Left View", image.get_data()) #dislay left image to cv2
            cv2.waitKey(10)
            cv2.imshow("Depth View", depth.get_data()) #dislay depth image to cv2
            cv2.waitKey(10)
            left_path = f'{colour_path}/colour_{svo_position}.png'
            dep_path = f'{depth_path}/depth_{svo_position}.tiff'
            img = image.write(left_path)
            dep = depth.write(dep_path)
            if img == sl.ERROR_CODE.SUCCESS:
                print("Saved image : ",left_path)
            else:
                print(f'Something wrong happened in image {svo_position} saving... ')
            if dep == sl.ERROR_CODE.SUCCESS:
                print("Saved depth : ",dep_path)
            else:
                print(f'Something wrong happened in depth {svo_position} saving... ')

            # # Point Cloud
            # zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
            # ply_path = f'{output_path}/zed_point_cloud.ply'
            # point_cloud.write(ply_path);

            # # JSON info
            # error, point_cloud_value = point_cloud.get_value(x, y)
            # x = point_cloud_value[0]
            # y = point_cloud_value[1]
            # z = point_cloud_value[2]

            # # Distance to an object
            # if math.isfinite(point_cloud_value[2]):
            #     distance = distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] + 
            #                                     point_cloud_value[1] * point_cloud_value[1] + 
            #                                     point_cloud_value[2] * point_cloud_value[2])
            #     print(f"Distance to Camera at {{{x};{y}}}: {distance}")
            # else : 
            #     print(f"The distance can not be computed at {{{x};{y}}}")

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