import numpy as np

class TransitionModel:
    
    def __init__(self):
        pass
    
    def get_noise(self, delta: float) -> np.ndarray:
        """Get the amount of assumed state transition noise as a covariance matrix.

        Parameter
        ---------
        delta : float
          how much time will pass in the next timestep
        
        Return
        ------
        Q : np.ndarray
          covariance matrix of gaussian transition noise
        """
        raise NotImplementedError("This method is supposed to be overidden")
    
    def transition(self, states: np.ndarray, noise: np.ndarray, delta: float) -> np.ndarray:
        """Transition some given state and noise samples.

        Parameter
        ---------
        states : np.ndarray
          state samples
        noise : np.ndarray
          noise samples
        delta : float
          how much time to pass

        Return
        ------
        out_states : np.ndarray
          array of same size as input states, transitioned through the non-linearity
        """
        raise NotImplementedError("This method is supposed to be overidden")

class AdditiveNormalNoiseTransitionModel(TransitionModel):
    def __init__(self):
        pass
    def transition(self, states, delta: float) -> np.ndarray:
        """Transition some given state by a time delta.

        Noise is considered additive, and is simply added onto the covariance matrix
        after the measurement model has been applied.

        This means that the get_noise() implementation must return a covariance matrix
        with compatible shape to the state vectors.

        For parameters and returns, see the transition() function in TransitionModel.
        """
        raise NotImplementedError("This method is supposed to be overidden")
