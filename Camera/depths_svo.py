#!/usr/bin/env python

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
import pyzed.sl as sl

# Initialise objects
depth_map = sl.Mat()
zed = sl.Camera()

# Create a InitParameters object and set configuration parameters
def init(svo_file):
    init_params = sl.InitParameters()
    init_params.set_from_svo_file(svo_file)
    init_params.camera_disable_self_calib = True
    init_params.depth_mode = sl.DEPTH_MODE.QUALITY  # New cameras (ZED2) use ULTRA depth mode | Old cameras (Previous firmware) use QUALITY
    init_params.coordinate_units = sl.UNIT.MILLIMETER  # Use meter units (for depth measurements)
    
    status = zed.open(init_params)
    if status != sl.ERROR_CODE.SUCCESS: #Ensure the camera opened succesfully 
        print("SVO file Open", status, "Exit program.")
        exit(1)
    return

def distance(svo_place, coord_x, coord_y):
    while True:  # for 'q' key
        zed.set_svo_position(int(svo_place))
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
            status_depth, depth_value = depth_map.get_value(coord_x, coord_y)
            return depth_value
        
def close_zed():
    zed.close()
    return