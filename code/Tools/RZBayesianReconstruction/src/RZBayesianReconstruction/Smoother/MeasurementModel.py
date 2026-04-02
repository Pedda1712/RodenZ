import numpy as np

class MeasurementModel:
    
    def __init__(self):
        pass
    
    def measure(self, states: np.ndarray, noises: np.ndarray) -> np.ndarray:
        """Produce measurements out of some state samples and noises.

        Parameter
        ---------
        states : np.ndarray
          state samples to measure
        noises : np.ndarray
          samples of measurement noise for each state

        Return
        ------
        measurements : np.ndarray
          measurement of state and noise samples
        """
        raise NotImplementedError("This method is supposed to be overridden")

class AdditiveNormalNoiseMeasurementModel(MeasurementModel):
    def __init__(self):
        pass
    def measure(self, states: np.ndarray) -> np.ndarray:
        """Produce measurements out of some state samples.

        Noise is considered additive, and is simply added onto the covariance matrix
        after the measurement model has been applied.

        For parameters and returns, see measure() in MeasurementModel class
        """
        raise NotImplementedError("This method is supposed to be overridden")
