## 3D Reconstruction based on Bayesian Smoothing
3D Reconstruction of Rodent Keypoints based on Bayesian Smoothing
to integrate temporal context into the reconstruction process directly.

This approach is also somewhat robust to errors in camera extrinsics, 
as it can modify them during smoothing. In practice, this means that the
rough camera extrinsics from ```RZCameraExtrinsicsTool``` are accurate enough
to serve as input to this tool.

### Intended Use
After the radial distortion correction step has been applied, the output CSVs from 
that stage may be used as input for this tool to perform 3D reconstruction.

### Usage
```bash
rzbayesianreconstruction --camera-configurations \
	Cam1.json
	...
	CamN.json
--input-keypoints \
	cam1.csv
	...
	camN.csv
--smoothing-parameters path/to/smoothing.json \
--output triangulated_bayesian.csv \
--reprojection-output reprojections.csv \
--skeleton-configuration path/to/config.json \
--log-level INFO \
--fps 200 \
--max-length 2000
```
Examples for smoothing parameters used in the mouse setting and skeletal configuration may be found in the ```Examples/``` subdirectory (```Examples/smoothing_parameters.json```, and ```Examples/rodenz_config.json```).

Here is an explanation of each key in the smoothing parameters dict, that is saved as a JSON file for the ```--smoothing-parameters``` option:
```python
{
    "base_point_prior_variance": 30, # prior position variance of mouse in cm
    "base_point_prior_velocity_variance": 10, # prior velocity variance of mouse in cm/s
    "skeletal_point_prior_variance": 4, # prior position offset variance of skeletal points (i.e. 4cm from parent)
    "skeletal_point_prior_velocity_variance": 4,
    "camera_prior_variance": 0.1, # variance of prior camera positions in degrees (how much to trust user provided config)
    "camera_transition_variance": 0.001, # how fast the camera position can change between frames (random walk variance)
    "base_point_velocity_variance": 1, # how much the base point can transition in one frame (variance of random walk on velocity)
    "skeletal_point_velocity_variance": 10, # variance of random walk on offset velocities
    "high_likelihood_threshold_variance": [0.8, 1], # DLC likelihood > 0.8 => 1 pixel variance of observation
    "medium_likelihood_threshold_variance": [0.6, 6], # > 0.6 => 6 pixel variance
    "low_likelihood_threshold_variance": [0.5, 640], # > 0.5 => 640 pixel variance (non-informative)
    "camera_cage": 3 # e.g. each camera parameter is clipped into the [prior - 3°, prior + 3°] interval
}
```

Here is an explanation of each key in the skeletal configuration dict, that is saved as a JSON file for the ```--skeleton-configuration``` option:
```python
{
    "SkeletalBase": "Tail_Base", # What Keypoint is considered the 'base point'
    "KeypointNames": [ # Keypoint names (in order they appear as columns in DLC ouput csvs)
	"Snout",
	"Left_Ear",
	"Right_Ear",
	"Neck",
	"Back",
	"Tail_Base",
	"Tail_Mid",
	"Tail_Tip",
	"Shoulder_Left",
	"Elbow_Left",
	"Front_Paw_Left",
	"Shoulder_Right",
	"Elbow_Right"	,
	"Front_Paw_Right",
	"Hip_Left"	,
	"Knee_Left"	,
	"Hind_Paw_Left"	,
	"Hip_Right"	,
	"Knee_Right"	,
	"Hind_Paw_Right"
    ],
    "Skeleton": [ # connections between keypoints, denoted as [parent, child]
	["Tail_Base", "Back"],
	["Back", "Neck"],
	["Neck", "Snout"],
	["Neck", "Left_Ear"],
	["Neck", "Right_Ear"],
	["Neck", "Shoulder_Left"],
	["Neck", "Shoulder_Right"],
	["Shoulder_Left", "Elbow_Left"],
	["Elbow_Left", "Front_Paw_Left"],
	["Shoulder_Right", "Elbow_Right"],
	["Elbow_Right", "Front_Paw_Right"],
	["Tail_Base", "Tail_Mid"],
	["Tail_Mid", "Tail_Tip"],
	["Tail_Base", "Hip_Left"],
	["Tail_Base", "Hip_Right"],
	["Hip_Left", "Knee_Left"],
	["Knee_Left", "Hind_Paw_Left"],
	["Hip_Right", "Knee_Right"],
	["Knee_Right", "Hind_Paw_Right"]
    ]
}
```


#### Example
To reconstruct the first 2000 frames of the mouse setup:
```bash
rzbayesianreconstruction --camera-configurations \
	Examples/Camera/Rough/Cam1.json \
	Examples/Camera/Rough/Cam2.json \
	Examples/Camera/Rough/Cam3.json \
	Examples/Camera/Rough/Cam4.json \
--input-keypoints \
	Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingNov13shuffle1_snapshot_best-60.csv \
	Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingNov13shuffle1_snapshot_best-60.csv \
	Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam3DLC_Resnet50_temp_trainingNov13shuffle1_snapshot_best-60.csv \
	Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingNov13shuffle1_snapshot_best-60.csv \
--smoothing-parameters Examples/smoothing_parameters.json \
--output triangulated_bayesian.csv \
--reprojection-output reprojections.csv \
--skeleton-configuration Examples/rodenz_config.json \
--log-level INFO \
--fps 200 \
--max-length 2000
```
You can then use RZView3DCSV to view the contents of file ```triangulated_bayesian.csv```, or proceed with whatever use case you have in mind.

For additional informations about the full argument set and its purposes, run:
```bash
rzbayesianreconstruction --help
```
