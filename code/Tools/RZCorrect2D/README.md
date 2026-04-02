# Radial Distortion Correction Tool
A tool for removing radial distortion from 2D keypoints. Provided a CSV of DLC output and a camera parameters file, this tool will output a corrected CSV.

## Intended Use
After obtaining 2D trajectory CSVs from DLC, we need to remove the radial distortion to allow for accurate triangulation down the line. This tool takes
in such a distorted CSV and a camera configuration file, and outputs a corrected version

## Usage
```
rzcorrect2D --input /path/to/dlc.csv --output /path/to/save/to.csv --camera-parameters /path/to/camera/parameters.json
```
For an example camera parameter json, take a look at ```Examples/Camera/Rough/Cam1.json```.
