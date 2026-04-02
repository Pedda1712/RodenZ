# Reconstruct 4-camera setup
rzbayesianreconstruction --camera-configurations \
	config/Cam1.json \
	config/Cam2.json \
	config/Cam3.json \
	config/Cam4.json \
--input-keypoints \
	corrected/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam3DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
--smoothing-parameters config/smoothing_parameters_low_movement.json \
--output reconstructed/reconstructions_cam_1_low.csv \
--reprojection-output reconstructed/reprojections_cam_1_low.csv \
--skeleton-configuration config/skeleton.json \
--calibration-output reconstructed/cam_1_smoother_calibrations_low.toml \
--log-level INFO \
--fps 200 

rzbayesianreconstruction --camera-configurations \
	config/Cam1.json \
	config/Cam2.json \
	config/Cam3.json \
	config/Cam4.json \
--input-keypoints \
	corrected/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam3DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
--smoothing-parameters config/smoothing_parameters_low_movement.json \
--output reconstructed/reconstructions_cam_2_low.csv \
--reprojection-output reconstructed/reprojections_cam_2_low.csv \
--skeleton-configuration config/skeleton.json \
--calibration-output reconstructed/cam_2_smoother_calibrations_low.toml \
--log-level INFO \
--fps 200 

rzbayesianreconstruction --camera-configurations \
        config/Cam1.json \
        config/Cam2.json \
        config/Cam3.json \
        config/Cam4.json \
--input-keypoints \
	corrected/cam_3/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_3/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_3/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam3DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_3/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
--smoothing-parameters config/smoothing_parameters_low_movement.json \
--output reconstructed/reconstructions_cam_3_low.csv \
--reprojection-output reconstructed/reprojections_cam_3_low.csv \
--skeleton-configuration config/skeleton.json \
--calibration-output reconstructed/cam_3_smoother_calibrations_low.toml \
--log-level INFO \
--fps 200 

rzbayesianreconstruction --camera-configurations \
        config/Cam1.json \
        config/Cam2.json \
        config/Cam3.json \
        config/Cam4.json \
--input-keypoints \
	corrected/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam3DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
--smoothing-parameters config/smoothing_parameters_low_movement.json \
--output reconstructed/reconstructions_cam_4_low.csv \
--reprojection-output reconstructed/reprojections_cam_4_low.csv \
--calibration-output reconstructed/cam_4_smoother_calibrations_low.toml \
--skeleton-configuration config/skeleton.json \
--log-level INFO \
--fps 200 

# Reconstruct Three-Camera setup
rzbayesianreconstruction --camera-configurations \
	config/Cam1.json \
	config/Cam2.json \
	config/Cam4.json \
--input-keypoints \
	corrected/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
--smoothing-parameters config/smoothing_parameters_low_movement.json \
--output reconstructed/three_cams_reconstructions_cam_1_low.csv \
--reprojection-output reconstructed/three_cams_reprojections_cam_1_low.csv \
--skeleton-configuration config/skeleton.json \
--calibration-output reconstructed/three_cams_cam_1_smoother_calibrations_low.toml \
--log-level INFO \
--fps 200 

rzbayesianreconstruction --camera-configurations \
	config/Cam1.json \
	config/Cam2.json \
	config/Cam4.json \
--input-keypoints \
	corrected/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
--smoothing-parameters config/smoothing_parameters_low_movement.json \
--output reconstructed/three_cams_reconstructions_cam_2_low.csv \
--reprojection-output reconstructed/three_cams_reprojections_cam_2_low.csv \
--skeleton-configuration config/skeleton.json \
--calibration-output reconstructed/three_cams_cam_2_smoother_calibrations_low.toml \
--log-level INFO \
--fps 200 

rzbayesianreconstruction --camera-configurations \
        config/Cam1.json \
        config/Cam2.json \
        config/Cam4.json \
--input-keypoints \
	corrected/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	corrected/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
--smoothing-parameters config/smoothing_parameters_low_movement.json \
--output reconstructed/three_cams_reconstructions_cam_4_low.csv \
--reprojection-output reconstructed/three_cams_reprojections_cam_4_low.csv \
--calibration-output reconstructed/three_cams_cam_4_smoother_calibrations_low.toml \
--skeleton-configuration config/skeleton.json \
--log-level INFO \
--fps 200 
