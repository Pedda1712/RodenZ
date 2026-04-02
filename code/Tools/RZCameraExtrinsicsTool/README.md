# Camera Extrinsics Tool
A tool where the user controls a virtual camera and aligns it with a camera image drawn over the scene geometry to determine camera positioning priors.

## Intended Use
We do not have precise camera extrinsics parameters and treat them as optimization variables in some of our triangulation approaches. For this, it is still useful to get some prior information on the camera position. 

This tools makes the user align a virtual camera with an image from the physical one, thus determining a plausible camera position.

## Usage
After following the installation instructions from the README in the `code/` directory. Invoke as such in your virtual environment with installed RZ* packages:
```
rzcameraextrinsics --image path/to/image.png --output cameraName
```
The location parameters chosen by the user will be saved in `{cameraName}_positional_prior.json`, to be used later by the triangulation scripts.

Note that an end-user will normally not invoke this tool themselves. This tool is only supposed to be used within a guided setup process.

## Example
Run this tool with one of the included training images from the training pipeline examples:
```bash
rzcameraextrinsics --image ./Examples/DLCPipeline/labeled_data/Cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2/img002287.png --output Cam_2
```
Note that you'd prefer to run this on undistorted images, but currently we only have distorted examples in the repository.
