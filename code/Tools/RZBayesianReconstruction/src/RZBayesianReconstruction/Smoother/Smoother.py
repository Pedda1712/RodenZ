from .UKFObserver import UKFObserver
from .UKFPredictor import UKFPredictor
from .MeasurementModel import MeasurementModel
from .TransitionModel import TransitionModel

import numpy as np
from tqdm import tqdm

import time

import logging
logger = logging.getLogger(__name__)


"""
Implements a Rauch-Tung-Striebel Smoother with the
unscented transform used to estimate propagated or
measured distributions as gaussians.
"""

def RamConstructor(m):
    return []

class Smoother:
    predictor: UKFPredictor
    observer: UKFObserver
    prior_mean: np.ndarray
    prior_covariance: np.ndarray

    def __init__(self, measurement_model: MeasurementModel, transition_model: TransitionModel, prior_mean: np.ndarray, prior_covariance: np.ndarray):
        self.predictor = UKFPredictor(transition_model)
        self.observer = UKFObserver(measurement_model)
        self.prior_mean = prior_mean
        self.prior_covariance = prior_covariance

    def estimate_sequence(self, measurements: list[np.ndarray], measurement_covariances: list[np.ndarray], deltas: list[float], smoothed_means_output, smoothed_covariances_output, _id: int, storage_constructor = RamConstructor):
        """
        Perform state estimation over a sequence of measurements
        using Unscented RTS Smoothing.

        Parameters:
        -----------
        measurements : list[np.ndarray]
          list of state measurements
        measurement_covariances : list[np.ndarray]
          list of measurement covariance matrices
        deltas : list[float]
          time delays between measurement steps
        smoothed_means_output : list-like object with .append()
          that will have output saved into it:
          means of the estimated state distribution
          at every time step (in reverse order)
        smoothed_covariances_output : list-like object with .append()
          that will have output saved into it:
          covariance of the estimated state
          distribution at every time step (in reverse order)
        _id : int
          id (e.g. timestamp) of this run
          if results are swapped to disk temporarilly, the folders will
          carry this id in their name
        storage_constructor : Callable
          this will be used to initialize storage containers for
          the sequential probability distributions
          example: default will keep all intermediate results
                   in main memory, using ListShelf instead will
                   reduce RAM load
        """
        if len(measurements) != len(measurement_covariances):
            raise RuntimeError("need same amount of measurement and covariances")
        if len(measurements) != len(deltas):
            raise RuntimeError("need time delay between all measurements")
        
        # First, UKF pass, saving the filter distributions and predicted distributions
        logger.debug("Allocating temporary storage ...")
        
        mean = self.prior_mean
        cov = self.prior_covariance
        means = storage_constructor(f"_tmp_filter_means_{_id}")
        means.append(self.prior_mean)
        covs = storage_constructor(f"_tmp_filter_covariances_{_id}")
        covs.append(self.prior_covariance)
        predicted_means = storage_constructor(f"_tmp_filter_predicted_means_{_id}")
        predicted_covs = storage_constructor(f"_tmp_filter_predicted_covariances_{_id}")
        Ds = storage_constructor(f"_tmp_filter_current_and_predicted_covariances{_id}")

        todo = len(measurements)

        logger.info("Creating Filtering Distributions")
        for unfiltered, noise, dt in tqdm(zip(measurements, measurement_covariances, deltas), total = len(measurements)):
            predicted_mean, predicted_cov, D = self.predictor.predict(mean, cov, dt)
            predicted_means.append(predicted_mean)
            predicted_covs.append(predicted_cov)
            Ds.append(D)
            mean, cov = self.observer.observe(predicted_mean, predicted_cov, unfiltered, noise)
            means.append(mean)
            covs.append(cov)

        # Backward pass to integrate future information into past timesteps
        smoothed_means_output.append(means.pop()) # last filter distribution already has all information
        smoothed_covariances_output.append(covs.pop())

        logger.info("Smoothing over distributions ...")
        for _ in tqdm(range(len(means))):
            mk = means.pop()
            Pk = covs.pop()
            mk1_dash = predicted_means.pop()
            Pk1_dash = predicted_covs.pop()
            Dk1 = Ds.pop()
            mk1_s = smoothed_means_output[-1]
            Pk1_s = smoothed_covariances_output[-1]

            # Actual Smoothing equations are very simple:
            Gk = Dk1 @ np.linalg.pinv(Pk1_dash, hermitian = True) # smoother gain
            mk_s = mk + Gk @ (mk1_s - mk1_dash)
            Pk_s = Pk + Gk @ (Pk1_s - Pk1_dash) @ Gk.T
            
            smoothed_means_output.append(mk_s)
            smoothed_covariances_output.append(Pk_s)

        logger.debug("Clearing temporary arrays ...")
        means.clear()
        covs.clear()
        predicted_means.clear()
        predicted_covs.clear()
        Ds.clear()
        return
