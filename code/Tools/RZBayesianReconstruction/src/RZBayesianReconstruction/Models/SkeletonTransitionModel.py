import numpy as np

from RZBayesianReconstruction.Smoother import AdditiveNormalNoiseTransitionModel

class SkeletonTransitionModel(AdditiveNormalNoiseTransitionModel):
    """A simple linear first-order transition model."""
    
    Q: np.ndarray
    parameter_count: int
    camera_parameter_bounds: tuple[np.ndarray, np.ndarray]
    
    def __init__(self, velocity_variance: np.ndarray, camera_variance: np.ndarray, camera_parameter_bounds: tuple[np.ndarray, np.ndarray]):
        self.Q = np.diag(np.concatenate((np.zeros(velocity_variance.shape), velocity_variance, camera_variance)))
        self.parameter_count = len(velocity_variance)
        self.camera_parameter_bounds = camera_parameter_bounds

    def get_noise(self, delta) -> np.ndarray:
        return (delta * delta) * self.Q

    def transition(self, states: np.ndarray, delta: float) -> np.ndarray:
        new_states = states.copy()
        new_states[:, :self.parameter_count] += new_states[:, self.parameter_count:(self.parameter_count * 2)] * delta
        new_states[:, (self.parameter_count*2):] = np.clip(new_states[:, (self.parameter_count * 2):], self.camera_parameter_bounds[0], self.camera_parameter_bounds[1])
        return new_states
