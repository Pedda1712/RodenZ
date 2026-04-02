import numpy as np
import pandas as pd
import json

from RZBayesianReconstruction.Models import Observer, ObserverIntrinsics
from RZBayesianReconstruction.Skeleton import SkeletonParameterMaps, RodentSkeleton

import logging
logger = logging.getLogger(__name__)

def load_smoothing_parameters(smoothing_parameters: str) -> dict:
    with open(smoothing_parameters, "r") as f:
        return json.load(f)
    raise RuntimeError(f"could not load smoothing parameters from {smoothing_parameters}")

def load_skeleton(skeleton_configuration_path: str) -> RodentSkeleton:
    logger.debug(f"Load skeleton configuration from {skeleton_configuration_path}")
    with open(skeleton_configuration_path, "r") as f:
        config = json.load(f)
        points = config["KeypointNames"]
        skeleton = [[points.index(start), points.index(end)] for (start, end) in config["Skeleton"]]
        maps = SkeletonParameterMaps(points)
        base = config["SkeletalBase"]
        number_pre_base = points.index(base)
        number_post_base = len(points) - number_pre_base - 1
        return RodentSkeleton(points.index(base), len(points), skeleton), maps, number_pre_base, number_post_base, points
    raise RuntimeError(f"Failed loading skeleton from {skeleton_configuration_path}")

def load_and_preprocess_camera_measurements(csv_path: str, view_info: ObserverIntrinsics) -> tuple[np.ndarray, np.ndarray]:
    """Load one set of 2D measurements into a position array and likelihood array."""
    width =  view_info.resolution_x
    height = view_info.resolution_y
    skipframes = view_info.sync_skip

    logging.info(f"Starting to load {csv_path}")
    table = np.array(pd.read_csv(csv_path, header = None, low_memory = False))[3:, 1:].astype(np.double)
    table = table[skipframes:]

    indices = np.array([True] * table.shape[1])
    indices[2::3] = False

    xy = table[:, indices]
    likelihood = table[:, ~indices]

    # XY to NDC
    xy[:, 0::2] /= width
    xy[:, 1::2] /= height
    xy -= 0.5
    xy *= 2
    xy[:, 1::2] *= -1

    return xy, likelihood

def likelihoods_to_variances(likelihoods, observer_intrinsics, smoothing_parameters):
    def duplicate_likelihoods(likelihoods):
        duplicated = np.zeros((likelihoods.shape[0], likelihoods.shape[1]*2))
        full_indices = np.mod(np.arange(duplicated.shape[1]),2)
        duplicated[:,(full_indices == 0)] = likelihoods
        duplicated[:,(full_indices == 1)] = likelihoods
        return duplicated
    duplicated = duplicate_likelihoods(likelihoods)
    highest_indices = duplicated > smoothing_parameters["high_likelihood_threshold_variance"][0]
    higher_indices = duplicated > smoothing_parameters["medium_likelihood_threshold_variance"][0]
    lower_indices = duplicated > smoothing_parameters["low_likelihood_threshold_variance"][0]
    duplicated[:,:] = 100
    duplicated[lower_indices] = 2 * (smoothing_parameters["low_likelihood_threshold_variance"][1] / observer_intrinsics.resolution_x)
    duplicated[higher_indices] = 2 * (smoothing_parameters["medium_likelihood_threshold_variance"][1] / observer_intrinsics.resolution_x)
    duplicated[highest_indices] = 2 * (smoothing_parameters["high_likelihood_threshold_variance"][1] / observer_intrinsics.resolution_x)
    return duplicated

def load_measurements(csv_paths: list[str], view_infos: list[ObserverIntrinsics], smoothing_parameters: dict) -> tuple[np.ndarray, np.ndarray]:
    """Load measurements as 2D means in NDCs + diagonal of covariance matrix.

    Parameters
    ----------
    csv_paths: list[str]
      paths to the corrected CSVs
    view_infos: list[ObserverIntrinsics]
      resolution and sync-skip of the individual views, obtained by
      load_observers()
    smoothing_parameters: dict
      contains information about which DLC likelihood thresholds correspond
      to which pixel variances

    Return
    ------
    measurements : np.ndarray
      one row here are the concatenated 2D measurements
    variances : np.ndarray
      each element here denotes the variance of the corresponding
      element in the measurement array
    """
    measurements: list[np.ndarray] = []
    variances: list[np.ndarray] = []

    min_rows = None
    for csv_path, view_info in zip(csv_paths, view_infos):
        xy, likelihood = load_and_preprocess_camera_measurements(csv_path, view_info)
        logging.info(f"Loaded {xy.shape[0]} rows from {csv_path}.")
        if min_rows is None or xy.shape[0] < min_rows:
            min_rows = xy.shape[0]
        measurements.append(xy)
        variances.append(likelihoods_to_variances(likelihood, view_infos[0], smoothing_parameters))
    
    for i in range(len(measurements)):
        measurements[i] = measurements[i][:min_rows, :]
        variances[i] = variances[i][:min_rows, :]

    return np.hstack(measurements), np.hstack(variances)

def get_intrinsics_from_fov(fov_deg, width, height):
    f = (width / 2) / np.tan(np.radians(fov_deg / 2))
    K = np.array([
        [f, 0, width/2],
        [0, f, height/2],
        [0, 0, 1]
    ])
    return K

def fetch_distortion_parameters(d):
    return np.array([
        d["distortion"]["k1"],
        d["distortion"]["k2"],
        d["distortion"]["p1"],
        d["distortion"]["p2"],
        d["distortion"]["k3"]
    ]), get_intrinsics_from_fov(d["camera_fov"], d["resolution"]["x"], d["resolution"]["y"])

def load_observers(camera_configuration_paths: list[str], synch_skips: list[int] = None) -> tuple[list[Observer], list[ObserverIntrinsics]]:
    """Load camera configurations."""
    
    if synch_skips is None:
        synch_skips = [0] * len(camera_configuration_paths)
    if len(synch_skips) != len(camera_configuration_paths):
        raise RuntimeError("Need same number of synch skips and camera configuration paths!")

    observers: list[Observer] = []
    intrinsics: list[ObserverInstrinsics] = []
    distortion_parameters: list[tuple[np.array, np.array]] = []
    for configuration_path, synch_skip in zip(camera_configuration_paths, synch_skips):
        logger.debug(f"Attempting to load {configuration_path} with skip {synch_skip} ...")
        with open(configuration_path, "r") as file:
            camera_data = json.load(file)
            observer = Observer(
                camera_dist = camera_data["camera_dist"],
                camera_pitch = camera_data["camera_pitch"],
                camera_yaw = camera_data["camera_yaw"],
                camera_fov = camera_data["camera_fov"],
                camera_fine_pitch = camera_data["camera_fine_pitch"],
                camera_fine_yaw = camera_data["camera_fine_yaw"],
                camera_fine_roll = camera_data["camera_fine_roll"],
            )
            observer_intrinsics = ObserverIntrinsics(
                resolution_x = camera_data["resolution"]["x"],
                resolution_y = camera_data["resolution"]["y"],
                sync_skip = synch_skip
            )
            observer_distortion_parameters = fetch_distortion_parameters(camera_data)
            logger.debug(f"Loading camera configuration {configuration_path} with skip {synch_skip} ...")
            observers.append(observer)
            intrinsics.append(observer_intrinsics)
            distortion_parameters.append(observer_distortion_parameters)
            
    if len(observers) != len(camera_configuration_paths):
        raise RuntimeError("Loading failed for some cameras!")
    return observers, intrinsics, distortion_parameters
