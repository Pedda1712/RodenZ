# Camera Calibration Tool
DISCLAIMER: This tool is only needed if you wish to not use the bayesian smoothing approach of ``rzbayesianreconstruction``.

A CLI tool that performs automatic or manual **Charuco-based camera calibration** for multi-camera setups, so it can be used in ``rztriangulate``.

## Intended Use
This tool provides a script-based method to calibrate cameras.
It supports:

- Automatic ArUco dictionary detection
- Automatic estimation of marker and square pixel sizes
- Optional manual board configuration (if known board data)
- Fisheye or standard lens models
- Preload exisiting parameters for calibration warum-up
- Multi-camera calibration using `aniposelib`

## Usage
You may provide manual Charuco board parameters or let the system infer them automatically from your calibration videos.

---

## Example Calls

### Case 1: Fully Automatic Mode  
Dictionary and board geometry (marker/square size) are inferred from the first calibration video.
Auto mode assumes a checker to sqaure ratio of 0.75.

```bash
rzcal \
    --calibration-vids /path/to/cam0.mp4 /path/to/cam1.mp4 \
    --no-fisheye \
    --output /path/to/save\
    --auto-board
```

### Case 2: Manual Mode  
No auto-detection. All board parameters must be provided.

```bash
rzcal \
    --calibration-vids /path/to/cam0.mp4 /path/to/cam1.mp4 \
    --no-fisheye \
    --output /path/to/save \
    --squaresX 7 \
    --squaresY 4 \
    --square-length 30.0 \
    --marker-length 22.0 \
    --dictionary DICT_6X6_100
```

### Case 3: Fisheye Calibration  
For wide-angle cameras.

```bash
rzcal \
    --calibration-vids /path/to/cam0.mp4 /path/to/cam1.mp4 \
    --fisheye \
    --output /path/to/save \
    --auto-board
```

### Case 4: Warm-up with prior calibration data  
For wide-angle cameras.

```bash
rzcal \
    --calibration-vids /path/to/cam0.mp4 /path/to/cam1.mp4 \
    --no-fisheye \
    --output /path/to/save \
    --auto-board \
    --initial \
    --initial-file /path/to/toml 
```

---

## Getting Help
To view the full argument list:

```bash
rzcal --help
```

## Example Usage
Example command to run the calibration based on example data given in the root directory.

### Without warm-up
```bash
rzcal --calibration-vids Examples/Calibration/videos/cam_1.avi  Examples/Calibration/videos/cam_3.avi  --auto-board --no-fisheye  --output ./
```

### With warm-up
```bash
rzcal --calibration-vids Examples/Calibration/videos/cam_1.avi  Examples/Calibration/videos/cam_3.avi  --auto-board --no-fisheye  --output ./ \
--initial --initial-file Examples/Calibration/calibration.toml
```