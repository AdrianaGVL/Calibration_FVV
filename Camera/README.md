# FVV CALIBRATION

## Camera - Reording - Frames & Depth
Scripts for working with the ZED SDK. Getting frames, depth and intrinsic parameters are the main objectives of these scripts. Recording is also considered.

* **Frames & Intrinsic parameters:** The scripts *images_svo.py* and *images_svo_e.py* extract the intrinsic parameters and frames from SVO file.
  * **Images SVO (Error Study):** The script *images_svo.py* is used for those SVOs that were recorded for the depth error analysis. This script returns a JSON file with the intrinsic parameters that OpenMVG will use later, and the colour frames of the left camera.
  * **Images SVO (Extrinsic calibration):** The script *images_svo_e.py* is used for those SVO that were recorded for the extrinsic calibration. This script returns a txt file with the info per frame (each camera has it owns intrinsic parameters and OpenMVG needs to know them for each frame), the colour frames of the left and right camera.
* **Depth:** In this case, the only script used to extract depth values is *depths_svo.py*. This script returns the depth value of a pair of pixel coordinates.
* **Recording:** The depth error analysis SVO files are always recorded with the ZED Explorer app from the ZED SDK, as the laptop used has no GPU. However, if a laptop with GPU is used, or for the extrinsic calibration, the script *cam_recording.py* should be used. This script record and save it as a SVO file.