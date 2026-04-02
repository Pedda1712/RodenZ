from dataclasses import dataclass
import numpy as np

import logging
logger = logging.getLogger(__name__)

@dataclass
class SigmaPointGenerationConfig:
    alpha: float = 1
    beta: float = 0
    kappa: float = -1

def sigma_points(mean: np.ndarray, cov: np.ndarray, parameters: SigmaPointGenerationConfig = SigmaPointGenerationConfig()) -> tuple[list[np.ndarray], list[float], list[float]]:
    """
    Calculate Sigma Points of the Unscented Transform according to [Särkkä2013]
    """
    n = mean.shape[0]
    
    lam = (parameters.alpha**2)*(n + parameters.kappa) - n
    fac = np.sqrt(n + lam)
    
    n_points = 2 * n + 1
    X = [np.zeros(n) for _ in range(n_points)]
    Wm = [1/(2*n + 2*lam)] * n_points
    Wc = [1/(2*n + 2*lam)] * n_points
    Wm[0] = lam / (n + lam)
    Wc[0] = lam / (n + lam) + (1 - parameters.alpha**2 + parameters.beta)

    P = None
    while True:
        try:
            P = np.linalg.cholesky(cov)
            break
        except:
            # fix that shit
            logger.error("cholesky error, adding offset and trying again")
            vals = np.linalg.eigvalsh(cov)
            logger.error("eigval profile that caused error: ")
            logger.error(vals)
            minimal_value = vals.min()
            minimal_value = np.abs(minimal_value) + 1e-5
            cov = (cov + cov.T) * 0.5 + np.eye(cov.shape) * minimal_value
    X[0] = mean.copy()

    for i in range(n):
        idx = i + 1
        X[idx] = mean + fac * P[:, i]
        X[idx + n] = mean - fac * P[:, i]
    return X, Wm, Wc

def transformed_sigma_points_to_gaussian(X: list[np.ndarray], Wm: list[float], Wc: list[float], X_old: list[np.ndarray] = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    m = (np.array(X) * np.array(Wm).reshape(-1, 1)).sum(axis=0)
    centered_X = (np.array(X) - m)
    Pk = centered_X.T @ (centered_X * np.array(Wc).reshape(-1, 1))
    
    if X_old is None:
        return m, Pk, None
    else:
        # for the observations: also calculate covariance of predicted state and observations
        X_old = np.array(X_old)
        m_old = (X_old * np.array(Wm).reshape(-1, 1)).sum(axis=0)
        X_old_centered = (X_old - m_old)
        Ck = X_old_centered.T @ (centered_X * np.array(Wc).reshape(-1, 1))
        return m, Pk, Ck

def extend_state_by_normal_noise(mk, Pk, Q):
    stateshape = Pk.shape[0]
    noisedim = Q.shape[0]
    Pk_ex = np.block([
        [Pk, np.zeros((stateshape, noisedim))],
        [np.zeros((noisedim, stateshape)), Q]
    ])
    mk_ex = np.append(mk, np.zeros(noisedim))
    return mk_ex, Pk_ex
