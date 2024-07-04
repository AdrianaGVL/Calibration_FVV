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

# Libraries
import sys
import pyzed.sl as sl
from signal import signal, SIGINT
import argparse 
import os 

cam = sl.Camera()

#Handler to deal with CTRL+C properly
def handler(signal_received, frame):
    cam.disable_recording()
    cam.close()
    sys.exit(0)

signal(SIGINT, handler)

def main():
    
    init_paranms = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD1080, camera_fps=30, depth_mode=sl.DEPTH_MODE.QUALITY, camera_disable_self_calib=True, camera_image_flip=sl.FLIP_MODE.OFF, depth_stabilization=0)
    init_run = sl.RuntimeParameters(enable_depth=False)
    recording_param = sl.RecordingParameters(video_filename=opt.output_svo_file, compression_mode=sl.SVO_COMPRESSION_MODE.H264_LOSSLESS, target_framerate=30) # Enable recording with the filename specified in argument
    
    status = cam.open(init_paranms) 
    if status != sl.ERROR_CODE.SUCCESS: 
        print("Camera Open", status, "Exit program.")
        exit(1)
        
    err = cam.enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Recording ZED : ", err)
        exit(1)
        
    print("SVO is Recording, use Ctrl-C to stop.") # Start recording SVO, stop with Ctrl-C command
    frames_recorded = 0

    while True:
        if cam.grab(init_run) == sl.ERROR_CODE.SUCCESS : # Check that a new image is successfully acquired
            frames_recorded += 1
            print("Frame count: " + str(frames_recorded), end="\r")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_svo_file', type=str, help='Path to the SVO file that will be written', required= True)
    opt = parser.parse_args()
    if not opt.output_svo_file.endswith(".svo") and not opt.output_svo_file.endswith(".svo2"): 
        print("--output_svo_file parameter should be a .svo file but is not : ",opt.output_svo_file,"Exit program.")
        exit()
    main()