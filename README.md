# FVV CALIBRATION

***This branch is for working on the pepegotera computer.***
This project aims to study the depth estimation error of RGB-D cameras.

* **Cameras:**
  * The cameras used in this project were:
    * ZED
    * Necessary data:
      * Intrinsics (fx, fy, ppx, ppy) are needed, or at least, f. Look OpenMVG scripts.
      * Extrinsics (Camera poses)
* **External software:**
  * OpenMVG reconstruction is used as depth grund truth:
    * Scaling acording to real life distances is already implemented
    * Reprojection error is computed and only those point with 0'5 pixel error are used
  * OpenCV detecting corners function is used, beign those corners the ones used in Known Poses reconstruction (OpenMVG)
  
## Depth estimation study process

The *pipeline.sh* script is prepared to run the entire depth estimation study. However, each script is prepared to work on its own if the required files are available.

* **Configuration:** Any parameter, directory or file is defined in the *config_file.yml*. All scripts work with this file, so be careful when changing any parameter.
* **Data Structure:** Due to the fact that OpenMVG uses a JSON file to return the data, this is the file format used in this project.

### Directories and files structure

The following scheme uses the the variable's name used in *config_file.yml*.

```markdown
├── working_path/
│   ├── scene1/
│   │   ├── frames_folder
│   │   ├── out_path
│   │   │   ├── matches
│   │   │   ├── matches_known
│   │   │   ├── Reconstruction
│   │   │   ├── known_poses
│   │   │   │   ├── known_sfm_data
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
│   │   ├── calibration.json
│   ├── scene2/
│   ├── scene3/
│   ├── ...
```
