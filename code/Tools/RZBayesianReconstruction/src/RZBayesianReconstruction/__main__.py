import argparse
import logging
import time
import numpy as np
import pandas as pd
import toml

from pathlib import Path
from tqdm import tqdm

from RZBayesianReconstruction import load_measurements, load_observers, load_skeleton, load_smoothing_parameters, ListShelf, SkeletonTransitionModel, SkeletonTriangulationModel, Smoother, redistort, rodenz_camera_to_anipose_dict

def main():
    parser = argparse.ArgumentParser(description="3D reconstruction using bayesian smoothing.")

    # --- Input configuration ---
    parser.add_argument('--camera-configurations', type=Path, required=True, nargs="+",
                        help='List of CamX.json, must be exactly as many as in [input-keypoints], with the order of cameras matching.')
    parser.add_argument('--input-keypoints', type=Path, required=True, nargs="+",
                        help='List of (undistorted) 2D csvs, must match the count and camera order of [camera-configurations] parameter.')
    parser.add_argument('--synch-skip', type=int, nargs="+",
                        help='List of frames to skip for each camera, must match the count and order of [camera-configurations] parameter.')
    parser.add_argument('--skeleton-configuration', type=Path, required=True,
                        help='JSON file specifying joints between keypoints.')
    parser.add_argument('--smoothing-parameters', type=Path, required = True,
                        help='JSON file specifying smoothing parameters.')
    parser.add_argument('--max-length', type=int,
                        help='When specified, reconstruction is stopped after [max-length] amount of frames.')
    parser.add_argument('--fps', type=int, required = True,
                        help='Frames per second of the recording.')
    
    # --- Output Configuration ---
    parser.add_argument('--output', type=Path, required=True, help="Where to save output")
    parser.add_argument('--reprojection-output', type=Path, required=False, help="When set, outputs a CSV of 2D reprojections, which can be used by our evaluation tool to calculate ground truth errors.")
    parser.add_argument('--calibration-output', type=Path, required=False, help="When set, outputs an anipose camera calibration file from the mean smoothed camera extrinsics.")

    # --- Logging ---
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging verbosity level.')

    args = parser.parse_args()

    # -------------------------------------------------------------------------
    # Initialize logger
    # -------------------------------------------------------------------------
    level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(level=level,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)

    # -------------------------------------------------------------------------
    # Load camera priors, 2D measurements & skeleton
    # -------------------------------------------------------------------------
    smoothing_parameters = load_smoothing_parameters(args.smoothing_parameters)
    observers, view_info, distortion_parameters = load_observers(args.camera_configurations, args.synch_skip)
    measurements, variances = load_measurements(args.input_keypoints, view_info, smoothing_parameters)
    rodent_skeleton, skeleton_maps, number_pre_base, number_post_base, point_names = load_skeleton(args.skeleton_configuration)
    
    run_smoother(observers, view_info, distortion_parameters, measurements, variances, rodent_skeleton, skeleton_maps, number_pre_base, number_post_base, smoothing_parameters, args.output, args.reprojection_output, args.calibration_output, args.max_length, point_names, args.fps, logger)

def run_smoother(observers, view_info, distortion_parameters, measurements, variances, rodent_skeleton, skeleton_maps, number_pre_base, number_post_base, smoothing_parameters, output_path, reprojection_path, calibration_output_path, max_length, point_names, fps, logger):

    if max_length is None:
        max_length = len(measurements)
        
    logger.info(f"====== START SMOOTHING PIPELINE OF {max_length} MEASUREMENTS ======")
    
    delta = 1 / fps
    compiled_skeleton = rodent_skeleton.compile(skeleton_maps)

    _measurements = []
    _measurement_covariances = []
    _deltas = [delta] * max_length
    for i in range(max_length):
        _measurements.append(measurements[i,:])
        _measurement_covariances.append(np.diag(variances[i,:]))

    base_point_prior_variance = smoothing_parameters["base_point_prior_variance"] 
    base_point_prior_velocity_variance = smoothing_parameters["base_point_prior_velocity_variance"] 
    skeletal_point_prior_variance = smoothing_parameters["skeletal_point_prior_variance"] 
    skeletal_point_prior_velocity_variance = smoothing_parameters["skeletal_point_prior_velocity_variance"] 
    camera_prior_variance = smoothing_parameters["camera_prior_variance"] 
    
    camera_transition_variance = smoothing_parameters["camera_transition_variance"] *fps*fps
    base_point_velocity_variance = smoothing_parameters["base_point_velocity_variance"] *fps*fps
    skeletal_point_velocity_variance = smoothing_parameters["skeletal_point_velocity_variance"] *fps*fps
    
    camera_prior_mean = [observers[0].camera_fov] + sum([[o.camera_pitch, o.camera_yaw, o.camera_dist, o.camera_fine_pitch, o.camera_fine_yaw, o.camera_fine_roll, o.camera_fov] for o in observers[1:]], [])
    camera_upper_border = np.array(camera_prior_mean) + smoothing_parameters["camera_cage"]
    camera_lower_border = np.array(camera_prior_mean) - smoothing_parameters["camera_cage"]
    prior_mean = np.concatenate((np.zeros(((number_pre_base + number_post_base) * 3 + 3) * 2), camera_prior_mean))
    prior_covariance = np.diag(np.hstack((
        np.ones(number_pre_base*3) * skeletal_point_prior_variance,
        np.ones(3) * base_point_prior_variance,
        np.ones(number_post_base*3) * skeletal_point_prior_variance,
        np.ones(number_pre_base*3) * skeletal_point_prior_velocity_variance,
        np.ones(3) * base_point_prior_velocity_variance,
        np.ones(number_post_base*3) * skeletal_point_prior_velocity_variance,
        camera_prior_variance, # known observer FOV
        np.ones(7*(len(observers)-1))*camera_prior_variance,
    )))
    
    transition_variance = np.hstack((
        np.ones(number_pre_base*3) * skeletal_point_velocity_variance,
        np.ones(3) * base_point_velocity_variance,
        np.ones(number_post_base*3) * skeletal_point_velocity_variance,
    ))
    camera_transition_variance = np.ones(7 * (len(observers)-1) + 1) * camera_transition_variance

    transition_model = SkeletonTransitionModel(transition_variance, camera_transition_variance, (camera_lower_border, camera_upper_border))
    measurement_model = SkeletonTriangulationModel(observers[0], len(observers) - 1, compiled_skeleton, view_info[0].resolution_x / view_info[0].resolution_y)
    smoother = Smoother(measurement_model, transition_model, prior_mean, prior_covariance)

    _id = time.time_ns() // 1_000_000
    smoothed_means = ListShelf(f"_relative_smoothed_means_{_id}")
    smoothed_covariances = ListShelf(f"_relative_smoothed_covariances_{_id}")
    smoother.estimate_sequence(_measurements, _measurement_covariances, _deltas, smoothed_means, smoothed_covariances, _id, ListShelf)
    smoothed_means.flush()
    smoothed_covariances.flush()

    # convert to absolute positions and save to csv
    exec(compiled_skeleton[0], globals())
    to_absolute = eval(compiled_skeleton[1])

    def reproject(actual, guess):
        """
        Calculate mean squared reprojection error of one set of 2D keypoints
        actual: actual measurement coordinates (e.g. DLC Predictions or Ground Truth Annotations)
        guess: reprojections of smoother-inferred 3D coordinates
        """
        # NDC units ([-1, 1]) -> pixels
        guess[1::2] *= -1
        actual[1::2] *= -1
        
        actual += 1
        actual *= 0.5
        guess += 1
        guess *= 0.5

        for index, observer_intrinsics in enumerate(view_info):
            actual[(2*index)::(len(view_info)*2)] *= observer_intrinsics.resolution_x
            actual[(2*index + 1)::(len(view_info)*2)] *= observer_intrinsics.resolution_y
            guess[(2*index)::(len(view_info)*2)] *= observer_intrinsics.resolution_x
            guess[(2*index + 1)::(len(view_info)*2)] *= observer_intrinsics.resolution_y

        error = guess - actual
        error_x = error[0::2]
        error_y = error[1::2]
        squared_errors = error_x ** 2 + error_y ** 2
        twod_distances = np.sqrt(squared_errors)
        
        return twod_distances.mean(), guess

    csv_rows = []

    logger.info(f'Calculating mean camera extrinsics ...')
    camera_params = (len(observers) - 1) * 7 + 1
    mean_camera_params = np.zeros(camera_params)
    
    N = 0
    for index, m in enumerate(reversed(smoothed_means)):
        cam = m[(-camera_params):]
        mean_camera_params = (N / (N + 1)) * mean_camera_params + (1/(N+1)) * cam
        csv_rows.append(cam)
    
    logger.info(f'Mean camera extrinsics (Theta/Phi/Dist/Pitch/Yaw) for observers (1, ...) are \n {mean_camera_params}')
    

    known_observer = observers[0]
    mean_camera_params = np.concat((np.array([
        known_observer.camera_pitch,
        known_observer.camera_yaw,
        known_observer.camera_dist,
        known_observer.camera_fine_pitch,
        known_observer.camera_fine_yaw,
        known_observer.camera_fine_roll,
        mean_camera_params[0]
    ]), mean_camera_params[1:]))

    anipose_dicts = {}
    for camera_index, _view_info in enumerate(view_info):
        camera_name = f'cam_{camera_index}'
        start_index = camera_index * 7
        rz_cam = mean_camera_params[start_index:(start_index + 7)]
        cam_dict = rodenz_camera_to_anipose_dict(
            camera_name,
            rz_cam,
            _view_info,
            distortion_parameters[camera_index]
        )
        anipose_dicts[camera_name] = cam_dict

    if calibration_output_path:
        with open(calibration_output_path, 'w') as f:
            toml.dump(anipose_dicts, f)
            logger.info(f'Saved camera calibrations to {calibration_output_path}')
        pd.DataFrame(csv_rows).to_csv(f'{calibration_output_path}.trajectory.csv')
        
    logger.info(f'Calculating reprojections and saving 3D CSV ...')
    
    csv_rows = []
    reprojection_csv_rows = []

    errors = 0
    for index, m in tqdm(enumerate(reversed(smoothed_means)), total = (len(smoothed_means) - 1)):
        if index == 0:
            continue
        m_vector = m.reshape(1, -1) # 3D mean of posterior skeleton and camera extrinsics

        measurements = measurement_model.measure_without_noise(m_vector)[0] # measured mean without noise

        reprojections = reproject(_measurements[index - 1], measurements)
        
        errors += reprojections[0]

        twod_positions = reprojections[1].reshape(-1, 2)
        for camera_index in range(len(observers)):
            # apply assumed camera distortion again, because we compare against distorted GT in evalution ...
            camera_twod_positions = twod_positions[(camera_index * len(point_names)):((camera_index + 1) * len(point_names))]
            camera_twod_positions = redistort(camera_twod_positions, observers[camera_index], view_info[camera_index], distortion_parameters[camera_index])
            for point_index, point_name in enumerate(point_names):
                point = camera_twod_positions[point_index]
                reprojection_csv_rows.append([index - 1, camera_index, point_name, point[0], point[1]])

        m = m[:(len(m)//2)]
        csv_rows.append(to_absolute(m))
        
    errors /= (len(_measurements))
    logger.info(f"Average 2D distance of {errors} pixels on DLC predictions. (which may be larger than true average distance because of DLC outliers).")

    pd.DataFrame(csv_rows).to_csv(output_path, index = False)
    if reprojection_path:
        pd.DataFrame(reprojection_csv_rows).to_csv(reprojection_path, index = False, header = ["frame", "camera", "joint", "x", "y"])

    smoothed_means.clear()
    smoothed_covariances.clear()

if __name__ == "__main__":
    main()
