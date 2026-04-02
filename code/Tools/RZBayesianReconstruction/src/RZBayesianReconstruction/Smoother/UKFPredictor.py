import numpy as np

from .TransitionModel import TransitionModel, AdditiveNormalNoiseTransitionModel
from .SigmaPointGeneration import SigmaPointGenerationConfig, extend_state_by_normal_noise, sigma_points, transformed_sigma_points_to_gaussian

class UKFPredictor:
    f: TransitionModel
    config: SigmaPointGenerationConfig
    
    def __init__(self, f: TransitionModel, config: SigmaPointGenerationConfig = SigmaPointGenerationConfig()):
        self.f = f
        self.config = config
        
    def _predict(self, mk: np.ndarray, Pk: np.ndarray, delta: float) -> tuple[np.ndarray, np.ndarray]:
        mk_ex, Pk_ex = extend_state_by_normal_noise(mk, Pk, self.f.get_noise(delta))
        X, Wm, Wc = sigma_points(mk_ex, Pk_ex, self.config)
        
        X = np.array(X)
        state_dim = np.shape(mk)[0]
        states = X[:, :(state_dim)]
        noises = X[:, (state_dim):]
        
        Y = self.f.transition(states, noises, delta)

        m, P, D = transformed_sigma_points_to_gaussian(Y, Wm, Wc, states)
        return m, P, D
    
    def _predict_additive_noise(self, mk: np.ndarray, Pk: np.ndarray, delta: float) -> tuple[np.ndarray, np.ndarray]:
        X, Wm, Wc = sigma_points(mk, Pk, self.config)
        
        X = np.array(X)

        Y = self.f.transition(X, delta)

        m, P, D = transformed_sigma_points_to_gaussian(Y, Wm, Wc, X)

        P += self.f.get_noise(delta)
        
        return m, P, D
        
    def predict(self, mk: np.ndarray, Pk: np.ndarray, delta: float) -> tuple[np.ndarray, np.ndarray]:
        """
        Use the UT to approximate the distribution of the transformed
        gaussian variable by another gaussian distribution.

        Parameter
        ---------
        mk : np.ndarray
          mean vector of state distribution at time t
        Pk : np.ndarray
          covariance matrix of state distribution at time t
        delta : float
          time delta

        Return
        ------
        mk+1 : np.ndarray
          mean vector of predicted next distribution
        Pk+1 : np.ndarray
          covariance matrix of predicted next distribution
        """
        if isinstance(self.f, AdditiveNormalNoiseTransitionModel):
            return self._predict_additive_noise(mk, Pk, delta)
        return self._predict(mk, Pk, delta)
