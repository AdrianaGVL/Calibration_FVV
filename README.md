# FVV CALIBRATION

This project aims to study the depth estimation error of RGB-D cameras.

* **Cameras:**
  * The cameras used in this project were:
    * ZED / ZED 2 (Stereo Vision), from Stereolabs. This are the FVV Live system cameras.
    * Any other camera or system which returns colour and depth frames can be used if depth estimation error study is needed. Necessary data:
      * Intrinsics (fx, fy, ppx, ppy) are needed. Look OpenMVG scripts.
      * Extrinsics (Camera poses)
* **External software:**
  * OpenMVG reconstruction is used as depth grund truth:
    * Scaling acording to real life distances is already implemented
    * Reprojection error is computed
  * OpenCV detecting corners function is used, beign those corners the ones used in Known Poses reconstruction (OpenMVG)

## Directories and files structure

* **Data Structure:** Due to the fact that OpenMVG uses a JSON file to return the data, this is the file format used in this project along with YAML files.

The following scheme uses the the variable's name used in *usr_config_file.yml*.

```markdown
├── working_path/
│   ├── scene1/
│   │   ├── frames_folder
│   │   ├── out_path
│   │   │   ├── matches
│   │   │   ├── matches_known
│   │   │   ├── Reconstruction
│   │   │   ├── Reconstruction_for_known
│   │   │   │   ├── cloud_and_poses
│   │   │   │   ├── *Some other results*
│   │   │   ├── scale_data
│   │   │   │   ├── scales_file
│   │   │   │   ├── measures_file
│   │   │   │   ├── *Some other results*
│   │   │   ├── reprojection_path
│   │   │   │   ├── reprojection_file
│   │   │   │   ├── *Some other results*
│   │   │   ├── plane_path
│   │   │   │   ├── plane_file
│   │   │   │   ├── *Some other results*
│   │   │   ├── depth_path
│   │   │   │   ├──depth_file
│   │   │   │   ├── *Some other results*
│   │   │   ├── sfm_data_no_info.json
│   │   │   ├── sfm_data.json
│   │   │   ├── sfm_data_scaled.json
│   │   │   ├── cloud_and_poses_scaled.json
│   │   ├── svo_file.json
│   ├── scene2/
│   ├── scene3/
│   ├── ...
```

Each working directory is a camera, the working directory is named after the camera name and its serial number (e.g. ZED2_xxxxx). Any recorded video from the same camera will be moved to that working directory. Inside each working directory we will find more folders, one per video, named after the SVO file name.

### NOTE

Due to some hardware and software limitations, the use of dockers was necessary in the computer used to develop this code. If this is not necessary, simply run each script without the docker paths.

## Depth estimation study process

The *pipeline.sh* script is prepared to run the entire depth estimation study. However, each script is prepared to work on its own if the required files are available.

* **Configuration:** Any parameter, directory or file is defined in the *usr_config_file.yml*. All scripts work with this file, so be careful when changing any parameter. **IMPORTANT:** If the ZED SDK is used in orer to extract frames, use the file *config.yml*

###### Example of use - Error study

```bash
./pipeline.sh configs/usr_config_file.yml
```

## Extrinsic Calibration

The *extrinsics_pipeline.sh* script is prepared to run the entire depth estimation study. However, each script is prepared to work on its own if the required files are available.

* **Configuration:** Any parameter, directory or file is defined in the *e_config.yml*. All scripts work with this file, so be careful when changing any parameter. **IMPORTANT:** If the ZED SDK is used in orer to extract frames, use the file *config.yml*

###### Example of use - Extrinsics

```bash
./extrinsics_pipeline.sh configs/e_config.yml
```
