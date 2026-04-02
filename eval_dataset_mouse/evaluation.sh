#!/usr/bin/env bash
export QT_QPA_PLATFORM=offscreen
export MPLBACKEND=Agg

#------------------------------------------------------------------
# 3 Cam – Board-based Bundle Adjustment
#------------------------------------------------------------------

rzplot \
  --rp \
    reconstructed/three_cams_reprojections_cam_1_ba_board.csv \
    reconstructed/three_cams_reprojections_cam_2_ba_board.csv \
    reconstructed/three_cams_reprojections_cam_4_ba_board.csv \
  --gt \
    ground_truth/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1/CollectedData_Knorrsche.csv \
    ground_truth/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2/CollectedData_Knorrsche.csv\
    ground_truth/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4/CollectedData_Knorrsche.csv \
  --cams 0 1 2 \
  --out plots/three_cams_ba_board 

#------------------------------------------------------------------
# 3 Cam – Animal-based Bundle Adjustment
#------------------------------------------------------------------


rzplot \
  --rp \
    reconstructed/three_cams_reprojections_cam_1_ba_animal.csv \
    reconstructed/three_cams_reprojections_cam_2_ba_animal.csv \
    reconstructed/three_cams_reprojections_cam_4_ba_animal.csv \
  --gt \
    ground_truth/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1/CollectedData_Knorrsche.csv \
    ground_truth/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2/CollectedData_Knorrsche.csv\
    ground_truth/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4/CollectedData_Knorrsche.csv \
  --cams 0 1 2 \
  --out plots/three_cams_ba_animal

#------------------------------------------------------------------
# Smoothing Start – Animal-based Bundle Adjustment
#------------------------------------------------------------------

  rzplot \
  --rp \
    reconstructed/four_cams_reprojections_cam_1_ba_animal.csv \
    reconstructed/four_cams_reprojections_cam_2_ba_animal.csv \
    reconstructed/four_cams_reprojections_cam_3_ba_animal.csv \
    reconstructed/four_cams_reprojections_cam_4_ba_animal.csv \
  --gt \
    ground_truth/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1/CollectedData_Knorrsche.csv \
    ground_truth/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2/CollectedData_Knorrsche.csv\
    ground_truth/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam3/CollectedData_Knorrsche.csv \
    ground_truth/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4/CollectedData_Knorrsche.csv \
  --cams 0 1 2 3 \
  --out plots/four_cams_ba_animal

#------------------------------------------------------------------
# 3 Cam Smoothing 
#------------------------------------------------------------------
  rzplot \
  --rp \
    reconstructed/three_cams_reprojections_cam_1_low.csv \
    reconstructed/three_cams_reprojections_cam_2_low.csv \
    reconstructed/three_cams_reprojections_cam_4_low.csv \
  --gt \
    ground_truth/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1/CollectedData_Knorrsche.csv \
    ground_truth/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2/CollectedData_Knorrsche.csv\
    ground_truth/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4/CollectedData_Knorrsche.csv \
  --cams 0 1 2 \
  --out plots/three_cams_smoothing

#------------------------------------------------------------------
# 4 Cam Smoothing 
#------------------------------------------------------------------
  rzplot \
  --rp \
    reconstructed/reprojections_cam_1_low.csv \
    reconstructed/reprojections_cam_2_low.csv \
    reconstructed/reprojections_cam_3_low.csv \
    reconstructed/reprojections_cam_4_low.csv \
  --gt \
    ground_truth/Wildtype_EV_23_Vglut2-cre-eOPN3_M_Baseline_Opto-Off_3DOF_Cam1/CollectedData_Knorrsche.csv \
    ground_truth/Wildtype_EV_6_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam2/CollectedData_Knorrsche.csv\
    ground_truth/Wildtype_EV_14_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam3/CollectedData_Knorrsche.csv \
    ground_truth/Wildtype_EV_10_Vglut2-cre-somBiPOLES_M_Baseline_Opto-Off_3DOF_Cam4/CollectedData_Knorrsche.csv \
  --cams 0 1 2 3 \
  --out plots/four_cams_smoothing

#------------------------------------------------------------------
# Final shared plots
#------------------------------------------------------------------

  rzshare \
  --csvs \
    plots/three_cams_ba_board/global/l1_l2_distribution.csv \
    plots/three_cams_ba_animal/global/l1_l2_distribution.csv \
    plots/three_cams_smoothing/global/l1_l2_distribution.csv \
  --names Board-BA Animal-BA RodenZ \
  --metric l2 \
  --out plots/three_cam_hist_l2.png \
  --colors red green blue


  rzshare \
  --csvs \
    plots/four_cams_ba_animal/global/l1_l2_distribution.csv \
    plots/four_cams_smoothing/global/l1_l2_distribution.csv \
  --names Animal-BA RodenZ \
  --metric l2 \
  --out plots/four_cam_hist_l2.png \
  --colors green blue