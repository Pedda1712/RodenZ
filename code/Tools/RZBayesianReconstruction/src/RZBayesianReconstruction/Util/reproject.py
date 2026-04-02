import numpy as np
import cv2
from RZBayesianReconstruction.Models import Observer, ObserverIntrinsics

def redistort(points2d: np.ndarray, observer: Observer, view_info: ObserverIntrinsics, distortion_parameters: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    """Reproject 2D points into the camera plane to apply barrel distortion.

    Firstly, the screen space points are put into a plane in front of the camera.
    (This requires the camera's fov, and resolution)
    Then, opencv's projectPoints is called to reproject them into 2D points but
    with added barrel distortion.

    Parameters:
    -----------
    points2d : np.ndarray
      array of 2D points obtained from i.e. measurement model (in screen space)
    observer : Observer
      observer parametrization, only fov is used to determine coordinates in camera plane
    view_info : ObserverIntrinsics
      used to convert screen space to camera plane coordinates
    distortion_parameters : (coefficients, intrinsics)
      distortion polynomial coefficients, and camera intrinsic matrix, obtained from load_observers()

    Returns an array of exactly the same shape as points2d, but with added barrel distortion.
    """
    w_half = np.tan(np.radians(observer.camera_fov/2))
    ud = np.hstack((points2d, np.ones((points2d.shape[0],1))))
    ud[:, 0] = ud[:, 0] - view_info.resolution_x/2 
    ud[:, 0] = ud[:, 0] / (view_info.resolution_x * 0.5)
    ud[:, 0] *= w_half
    ud[:, 1] = ud[:, 1] - view_info.resolution_y/2 
    ud[:, 1] = ud[:, 1] / (view_info.resolution_x*0.5)
    ud[:, 1] *= w_half

    reproj_distorted, _ = cv2.projectPoints(ud.astype(np.double), np.eye(3), np.zeros(3), distortion_parameters[1], distortion_parameters[0])
    return reproj_distorted[:, 0, :]
    
