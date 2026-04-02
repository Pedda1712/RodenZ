# 3D Trajectory Visualisation Tool
A tool for visualizing inferred DLC trajectories and OpenCV undistortion.

## Intended Use
Visualizing 3D Triangulation output.

## Usage
```
rzview3Dcsv --csv /path/to/3D/csv --skeleton-definition /path/to/config.json [--rescale-to 10]
```
Where ```csv``` is set to the output of ```rztriangulate```. An example for a skeleton definition for rendering can be found in ```Examples/rodenz_config.json```.
```rescale-to``` can be used to scale up/down the 3D coordinate system.
