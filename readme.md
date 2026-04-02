# RodenZ : Probabilistic Triangulation of Moving Mice
RodenZ is a robust probabilistic triangulation method for tracking keypoints of any animal (originally developed for tracking mice keypoints), built on top of DeepLabCut 2D tracking, based on Bayesian Filtering and Smoothing. 

Whereas previous probabilistic approaches only integrated temporal context into animal positions (AcinoSet), RodenZ directly estimates its extrinsic and intrinsic camera parameters within the state model, integrating temporal context into the calibration process, resulting in a more robust holistic approach to the combined calibration-tracking problem.

This repository contains code for reproducing the results from our term paper at THWS, as well as the paper itself, and outlines how our approach may be deployed to new setups.

We demonstrated in our paper that our approach may lead to better results than the popular AniPose package in terms of reprojection error on few-calibration setups, such as the mouse setup we adressed directly in the paper.

As this was the result of a one-semester student project, there may be some rough edges, but we took care to provide our methodology in well-defined CLI steps and extracted specific (hyper)parameters of our setup into config files, so it should be more or less easily applied to novel setups. 

We recommend first reading the paper (```paper/``` subdirectory) to get an idea of how our method works.

## Deploying to a New Setup
RodenZ presupposes labeled training data in the DeepLabCut format (e.g. CollectedData_*.csv files) for each camera perspective you want to use. Everything else can be achieved by running one of our command-line tools.

Create a fresh python virtual environment, and install our packages to have these CLI tools available:
```bash
python -m venv ./venv
. venv/bin/activate
cd code
bash dev.sh
```

The following five steps are necessary for deploying RodenZ to new setups.

### Step 1 : Training DLC Predictors from Labeled Training Data
We have our own CLI wrapper around DLC (we wanted to automate training during development), the documentation is found in ```code/Tools/RZTrainDLC```. There is a ```rztrain``` tool for training networks and a ```rzinfer``` tool to produce 2D sequences from videos and save them in the CSV format.

We trained one DLC predictor for all views (performed better in our case), but you may choose to orchestrate different networks for different perspectives.

Then, produce 2D sequences for all camera perspectives and video sets you want to reconstruct using ```rzinfer```.

### Step 2 : Initial Camera Setup and Dealing with Radial Distortion
RodenZ produces accurate camera calibration (for everything except radial distortion) during inference, but requires sensible starting parameters. 

The ```rzcameraextrinsicstool``` was our way of finding starting extrinsic parameters. You choose one image from a camera, and align a virtual box (as our experiment took place in a box) with the image. The tool saves the extrinsic parameters in a JSON file. If your experiment does not have such an easily recognizable shape, you may choose the parameters in another ad-hoc scheme, or start from board calibrations that you put into this JSON format (see our paper for an explanation of our camera parametrization, and ```Examples/Camera/Rough/*.json``` files for how they are saved).

Currently, you need to add the radial distortion parameters and camera resolutions manually to these outputted JSON files (examples are found in ```Examples/Camera/Rough```, those are the starting configurations for our setup). Radial distortion parameters are in the OpenCV format, and may be obtained from board calibrations or manually (in our case, choosing them manually was easy as there are many straight edges visible in the frames).

Next, use the ```rzcorrect2D``` tool to remove radial distortion from the detected 2D keypoints that you inferred in the first step (docs of the command once more in ```code/Tools/RZCorrect2D``).

### Step 3 : Skeleton Configuration
RodenZ uses relative keypoint positions (e.g. the Snout's position is given relative to the Neck), you need to specify the relationship between the keypoints that you labeled previously into a JSON file. Copy the ```Examples/rodenz_config.json``` file (our skeleton for the mouse) and adapt it to your system. ATTENTION: the ```KeypointNames``` array MUST have the order of the columns in your ```CollectedData_*.csv``` files. The ```Skeleton``` array is made up of ```[nameOfStartingKeypoint, nameOfEndKeypoint]``` joint specifications.

### Step 4 : Smoother parameters
This is the most finnicky step, and you might need to circle back to it multiple times. Basically you need to specify all hyperparameters of the Bayesian Smoothing algorithm (prior position distribution of joints, transition variances, likelihood thresholds for the sensor model), as described in the paper.

These are our prior distributions for the mouse task:
```json
{
    "base_point_prior_variance": 15,
    "base_point_prior_velocity_variance": 10,
    "skeletal_point_prior_variance": 4, 
    "skeletal_point_prior_velocity_variance": 4,
    "camera_prior_variance": 5, 
    "camera_transition_variance": 0.00,
    "base_point_velocity_variance": 5,
    "skeletal_point_velocity_variance": 5,
    "high_likelihood_threshold_variance": [0.8, 1],
    "medium_likelihood_threshold_variance": [0.6, 6],
    "low_likelihood_threshold_variance": [0.5, 640],
    "camera_cage": 10
}
```

- ```base_point_prior_variance``` these are the variances (diagonal entries) (in cm) of the prior state distribution of the skeletal base point position (initial means are assumed to be 0)
- ```base_point_prior_velocity_variance``` variances (in cm/s) of the prior state distribution of the velocity of the skeletal base point (initial means are assumed to be 0)
- ```skeletal_*``` same as the previous two variables, but for the skeletal keypoints (which are relative positions and offsets to their given parent node)
- ```camera_prior_variance``` are the variance of the initial distribution of camera parameters
- ```base_point_velocity_variance```, ```skeletal_point_velocity_variance``` are the transition variances (i.e. how much can the velocity of a keypoint change in one second)
- ```*_likelihood_threshold_variance``` are the ```[DLC-likelihood, Pixel-Variance]``` tuples that specify our sensor model (e.g. with our parameters a DLC-likelihood greater than 0.8 has assumed pixel variance of 1)
- ```camera_cage``` defines an interval of permissible camera values, e.g. with ```camera_cage=10``` values are clipped after transition into +/- 10 of the starting parameters 

### Step 5 : Reconstruction
Use the ```rzbayesianreconstruction``` tool to read in all of you configuration files, corrected DLC predictions for each camera, camera extrinsic starting parameters, skeleton configuration and hyperparameters to produce a CSV of 3D keypoints (docs once more in ```code/Tools/RZBayesianReconstruction```).

You may use the ```rzview3Dcsv``` to view the results of reconstruction in 3D.

## Reproducing Paper Results
The ```eval_dataset_mouse/` subdirectory contains configuration files, bash scripts and execution instructions in the README file that reproduce the plots from our paper starting from the raw DLC output. As a result they may also be useful as examples on how to orchestrate a simple pipeline with our tools using bash scripts.
