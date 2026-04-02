# 2D Detection Visualisation Tool
A tool for visualizing inferred DLC trajectories and OpenCV undistortion.

## Intended Use
Checking DLC output and undistortion effect.

## Usage
```
rzview2Dcsv --video /path/to/video --csv /path/to/dlc/csv --camera-parameters /path/to/camera.json
```
Where ```camera-parameters``` is an optional parameter that, if set, leads to removing radial distortion from the video view according to the parameters in the camera json. For an example of the camera json files, take a look at ```Examples/Camera/Rough/Cam1.json```.

