#------------------------------------------------------------------
# 3 Cam - Board-based Bundle Adjustment
#------------------------------------------------------------------

# Cam 1
rztriangulate \
  --calibration config/calibration.toml \
  --keypoints \
    distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/three_cams_reconstructions_cam_1_ba_board.csv \
  --output-reprojected-2d reconstructed/three_cams_reprojections_cam_1_ba_board.csv \
  --triangulation-mode direct

# Cam 2
  rztriangulate \
  --calibration config/calibration.toml \
  --keypoints \
    distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/three_cams_reconstructions_cam_2_ba_board.csv \
  --output-reprojected-2d reconstructed/three_cams_reprojections_cam_2_ba_board.csv \
  --triangulation-mode direct

# Cam 4
  rztriangulate \
  --calibration config/calibration.toml \
  --keypoints \
    distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/three_cams_reconstructions_cam_4_ba_board.csv \
  --output-reprojected-2d reconstructed/three_cams_reprojections_cam_4_ba_board.csv \
  --triangulation-mode direct



#------------------------------------------------------------------
# 3 Cam - Board Start - Animal-based Bundle Adjustment
#------------------------------------------------------------------

# Cam 1
rztriangulate \
  --calibration config/calibration.toml \
  --keypoints \
    distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/three_cams_reconstructions_cam_1_ba_animal.csv \
  --output-reprojected-2d reconstructed/three_cams_reprojections_cam_1_ba_animal.csv \
  --triangulation-mode ba_before \
  --max-ba-frames 20000 \
 --output-calibration reconstructed/three_cams_cam_1_ba_animal_calibrations.toml

# Cam 2
  rztriangulate \
  --calibration config/calibration.toml \
  --keypoints \
    distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/three_cams_reconstructions_cam_2_ba_animal.csv \
  --output-reprojected-2d reconstructed/three_cams_reprojections_cam_2_ba_animal.csv \
  --triangulation-mode ba_before \
  --max-ba-frames 20000 \
 --output-calibration reconstructed/three_cams_cam_2_ba_animal_calibrations.toml

# Cam 4
  rztriangulate \
  --calibration config/calibration.toml \
  --keypoints \
    distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/three_cams_reconstructions_cam_4_ba_animal.csv \
  --output-reprojected-2d reconstructed/three_cams_reprojections_cam_4_ba_animal.csv \
  --triangulation-mode ba_before \
  --max-ba-frames 20000 \
 --output-calibration reconstructed/three_cams_cam_4_ba_animal_calibrations.toml

#------------------------------------------------------------------
# 4 Cam - Smoothing Start - Animal-based Bundle Adjustment
#------------------------------------------------------------------
# Cam 1
rztriangulate \
  --calibration reconstructed/cam_1_smoother_calibrations_low.toml \
  --keypoints \
    distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam3DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
    distorted/cam_1/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/four_cams_reconstructions_cam_1_ba_animal.csv \
  --output-reprojected-2d reconstructed/four_cams_reprojections_cam_1_ba_animal.csv \
  --triangulation-mode ba_before \
  --max-ba-frames 20000 \
  --output-calibration reconstructed/four_cams_cam_1_ba_animal_calibrations.toml

# Cam 2
  rztriangulate \
  --calibration reconstructed/cam_2_smoother_calibrations_low.toml \
  --keypoints \
    distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam3DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_2/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/four_cams_reconstructions_cam_2_ba_animal.csv \
  --output-reprojected-2d reconstructed/four_cams_reprojections_cam_2_ba_animal.csv \
  --triangulation-mode ba_before \
  --max-ba-frames 20000 \
  --output-calibration reconstructed/four_cams_cam_2_ba_animal_calibrations.toml

# Cam 3
  rztriangulate \
  --calibration reconstructed/cam_3_smoother_calibrations_low.toml \
  --keypoints \
    distorted/cam_3/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_3/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_3/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam3DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_3/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/four_cams_reconstructions_cam_3_ba_animal.csv \
  --output-reprojected-2d reconstructed/four_cams_reprojections_cam_3_ba_animal.csv \
  --triangulation-mode ba_before \
  --max-ba-frames 20000 \
  --output-calibration reconstructed/four_cams_cam_3_ba_animal_calibrations.toml

# Cam 4
  rztriangulate \
  --calibration reconstructed/cam_4_smoother_calibrations_low.toml \
  --keypoints \
    distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam1DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam3DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
	distorted/cam_4/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4DLC_Resnet50_temp_trainingDec31shuffle1_snapshot_best-100.csv \
  --output reconstructed/four_cams_reconstructions_cam_4_ba_animal.csv \
  --output-reprojected-2d reconstructed/four_cams_reprojections_cam_4_ba_animal.csv \
  --triangulation-mode ba_before \
  --max-ba-frames 20000 \
  --output-calibration reconstructed/four_cams_cam_4_ba_animal_calibrations.toml

