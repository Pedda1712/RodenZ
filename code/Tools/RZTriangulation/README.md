## CLI Triangulation tool
DISCLAIMER: This tool is only needed if you wish to not use the bayesian smoothing approach of ``rzbayesianreconstruction``.

A CLI tool for the non-bayesian alternative, which geometrical/numerical triangulates a given lists of inferred 2d CSV/H5 files (DLC Format), given a calibration file. Also allows the usage of a median filter for smoothing. 

### Intended Use
For using the triangulation, you first need a ``calibration.toml``, which you either need to provide, given the format of ``Examples/Calibration/calibration.toml``, or you can directly infer them from the RZCalibration Tool ``rzcal``.

### Usage
After following the installation instructions from the README in the code/ directory. Invoke as such in your virtual environment with installed RZ* packages:

#### Example Call
```bash
rztriangulate \
    --calibration <calibration.toml> \
    --input-keypoints <cam1.csv> <cam2.csv> \
    --triangulation-type (Simple)   \
    --median-size int     \
    --likelihood-threshold float  \   
    --log-level (INFO|DEBUG) \
```

For additional informations about the full argument set and its purposes, run:
```bash
rztriangulate --help
```

#### Example Usage
Example command to run the calibration based on example data given in the root directory.

```bash
rztriangulate --calibration Examples/Calibration/calibration.toml --keypoints Examples/Triangulation/Cam_1.csv Examples/Triangulation/Cam_3.csv --output ./
```