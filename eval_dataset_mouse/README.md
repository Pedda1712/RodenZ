# RodenZ Project Evaluation File Structure
What is in here from the start, and where does it come from:
- ```config/``` contains CamX.json (from RZCameraExtrinsicsTool), skeleton.json (hand-written), smoothing_parameters_*.json (hand-tuned on validation videos)
- ```distorted/``` contains DLC outputs of the video tracks EV_23, EV_6, EV_14, EV_10 (for which we have some ground truth labeled frames that werent used in training)
- ```ground_truth/``` contains ground truth 2d annotations of the video tracks EV_23, EV_6, EV_14, EV_10

These can be downloaded under: https://cloud.fiw.thws.de/s/7a7qn2bTEFRByst

After downloading, extract the ```config/```,```distorted/``` and ```ground_truth/``` folder inside this ( ```{project_root}/eval_dataset_mouse/```) directory.

## Running
You need the command line tools from the ```code/``` repository installed. The README in the project root has instructions for installation.

First, run:
```bash
./correct.sh
```
This undistorts the DLC outputs, i.e. it populates the ```corrected/``` subdirectory (our smoother required undistorted inputs).

Next, run:
```bash
./smoother_reconstruct_low.sh
```
This saves reconstructed 3D trajectories, reprojected 2D sequences, and extracted smoothed calibrations (for use with anipose) into the ```reconstructed/``` subdirectory.

Next, run:
```bash
./bundle_adjustment_reconstruct.sh
```
This saves reconstructed 3D trajectories, reprojected 2D sequences from AniPose BA into the ```reconstructed/``` subdirectory.

Finally, run:
```bash
./evaluation.sh
```
This saves reprojection-GT compared errors as histogram, violin, csv for each approach, cam and globally into the ```plots/``` subdirectory. Additionally, it creates shared histogram + KDE plots to visually compare the evaluated approaches.
