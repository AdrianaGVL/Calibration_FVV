# FVV CALIBRATION

## Error Study

The scripts for analyse the depth estimation error of the cameras.

* **Reconstruction Scaling:** Due to the arbitrary scale of the OpenMVG reconstruction, it needs to be scale with the corners of the chessboard. The scripts fro this task are *scale.py* and *rescale.py*.
  * **Scales:** Comparing the distance between corners in the reconstruction from known poses and the real distance, obtains the scale of the reconstruction.
  * **Rescale:** Multiply every camera center and point by the scale factor
* **Ground Truth validation:** In order to prove that OpenMVG is a valid ground truth, the scripts, *measures.py*, *plane3D.py* and *reprojection.py*, are used.
  * **Measures:** Returns the distance and angles error.
  * **Plane 3D:** Obtain the plane in which the corners are. The corners coordinates are the ones returned by OpenMVG from known poses. It also return two PLY files, one with the plane and one with the points (open them in the same Meshlab window).
  * **Reprojection:** Returns the reprojection error of te Known poses reconstruction.
* **Depth Error analysis:** Only two scripts are used, *depth.py* and *sistematic_error.py*. The script *depth_from_np.py* is the same as the *depth.py* one, but in this case the depth is read from a npy file.
  * *Depth:* Runs a loop for in which every keypoint is used. The depth obtained with OpenMVG and the depth return by the ZED is comapared. Returns a JSON file and some charts.
  * **Sistematic Error:** Takes all the recordings of the same camera and analyses all them together. Retunrs a dataframe and a chart.

## Error parametrisation

Once the depth analysis is complete, it is parameterised and the optimal is selected.

* **Parameterisation:** In this case one script is used, *ZED_parameterisation_one_by_one.py*. This script obtain the four polinomial equations, one per polinomial degree, from the first to the fourth grade.
* **Depth correction anlysis:** As before, one script is used, *correct_depth_each.py*. Correct the depth for each video using the polinomial equation for each video.
