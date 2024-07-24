# FVV CALIBRATION

## Dockerfiles

Due to the old version of Ubuntu on the computer in which the code was developed, a docker is required if a higher version of the ZED SDK is to be used.
Just download the docker file and run the following command:

```bash
docker build -f Dockerfile_ZEDv4 -t zed_sdk_v4
```

The code in this project is already prepared to work with this docker. Do not change the name of the example.
If your CUDA version is not 12.1.1, you may have problems with the docker, but try it anyway.
