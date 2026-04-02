import numpy as np

from .MeasurementModel import MeasurementModel, AdditiveNormalNoiseMeasurementModel
from .SigmaPointGeneration import SigmaPointGenerationConfig, extend_state_by_normal_noise, sigma_points, transformed_sigma_points_to_gaussian

class UKFObserver:
    h: MeasurementModel
    config: SigmaPointGenerationConfig
    
    def __init__(self, h: MeasurementModel, parameters: SigmaPointGenerationConfig = SigmaPointGenerationConfig()):
        self.h = h
        self.config = parameters

    def _observe(self, m_predict: np.ndarray, P_predict: np.ndarray, y_observe: np.ndarray, observation_uncertainty: np.ndarray):
        m_predict_ex, P_predict_ex = extend_state_by_normal_noise(m_predict, P_predict, observation_uncertainty)
        X, Wm, Wc = sigma_points(m_predict_ex, P_predict_ex, self.config)

        X = np.array(X)
        state_dim = m_predict.shape[0]
        states = X[:, :state_dim]
        noises = X[:, state_dim:]
        
        Y = self.h.measure(states, noises)

        mu, S, C = transformed_sigma_points_to_gaussian(Y, Wm, Wc, states)

        # now the rules for gaussian conditioning apply
        K = C @ np.linalg.pinv(S, hermitian=True) # filter gain
        m = m_predict + K @ (y_observe - mu)
        P = P_predict - K @ S @ K.T
        return m, P

    def _observe_additive_noise(self, m_predict: np.ndarray, P_predict: np.ndarray, y_observe: np.ndarray, observation_uncertainty: np.ndarray):
        X, Wm, Wc = sigma_points(m_predict, P_predict, self.config)

        X = np.array(X)        
        Y = self.h.measure(X)

        mu, S, C = transformed_sigma_points_to_gaussian(Y, Wm, Wc, X)

        S += observation_uncertainty

        # now the rules for gaussian conditioning apply
        K = C @ np.linalg.pinv(S, hermitian=True) # filter gain
        m = m_predict + K @ (y_observe - mu)
        P = P_predict - K @ S @ K.T
        return m, P

    def observe(self, m_predict: np.ndarray, P_predict: np.ndarray, y_observe: np.ndarray, observation_uncertainty: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Turn predictive distributions at time t into corrected distributions.

        Parameter
        ---------
        m_predict : np.ndarray
          mean vector of the predicted distribution
        P_predict : np.ndarray
          covariance matrix of the predicted distribution
        y_observe : np.ndarray
          observation made at current time step
        observation_uncertainty : np.ndarray
          covariance matrix of observation

        Return
        ------
        mk : np.ndarray
          the mean vector of the distribution corrected for the measurement
        Pk : np.ndarray
          the covariance matrix of the distribution corrected for the measurement
        """
        if isinstance(self.h, AdditiveNormalNoiseMeasurementModel):
            return self._observe_additive_noise(m_predict, P_predict, y_observe, observation_uncertainty)
        return self._observe(m_predict, P_predict, y_observe, observation_uncertainty) # non-additive (transformed) noise variable
