import numpy as np
import cv2
from RZBayesianReconstruction.Models import ObserverIntrinsics

def np_rotate_y(angle_rad):
    return np.array([
        [np.cos(angle_rad), 0, np.sin(angle_rad), 0],
        [0, 1, 0, 0],
        [-np.sin(angle_rad), 0, np.cos(angle_rad), 0],
        [0, 0, 0, 1],
    ])
def np_rotate_x(angle_rad):
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(angle_rad), -np.sin(angle_rad), 0],
        [0, np.sin(angle_rad), np.cos(angle_rad),  0],
        [0, 0, 0, 1],
    ])
def np_rotate_z(angle_rad):
    return np.array([
        [np.cos(angle_rad), -np.sin(angle_rad), 0, 0],
        [np.sin(angle_rad), np.cos(angle_rad),  0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])
def np_translate_z(dist):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, dist],
        [0, 0, 0, 1]
    ])
def np_radians(deg):
    return deg * (3.141/180)

def get_np_viewpoint(pitch, yaw, dist, fine_pitch, fine_yaw, fine_roll):
    mat1 = np_rotate_y(np_radians(yaw))
    mat2 = np_rotate_x(np_radians(pitch))
    mat3 = np_translate_z(-dist)
    mat4 = np_rotate_y(np_radians(fine_yaw))
    mat5 = np_rotate_x(np_radians(fine_pitch))
    mat6 = np_rotate_z(np_radians(fine_roll))
    return mat6 @ mat5 @ mat4 @ mat3 @ mat2 @ mat1

def get_np_ndc_cam(fov_deg, width, height):
    # camera coordinates to homogenous NDC (-1 to 1 space)
    f = 1 / np.tan(np_radians(fov_deg)/2)
    a = width / height
    return np.array([
        [f / a, 0, 0],
        [0, f, 0],
        [0, 0, 1] # view matrix follows GL convention of negative Z viewing direction
    ])

def get_ndc_to_screen_space(width, height):
    return np.array([
        [width/2, 0, width/2],
        [0, height/2, height/2], # flip, screen space runs top to bottom
        [0, 0, 1]
    ])

def get_invert_x_and_z():
    return np.array([
        [1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1]
    ])

def rodenz_camera_to_anipose_dict(name: str, rz_cam: np.ndarray, view_info: ObserverIntrinsics, distortion_parameters: tuple[np.ndarray, np.ndarray]):
    """Theta/Phi/Dist/Pitch/Yaw to anipose camera parameters.

    Parameters:
    -----------
    name : str
      name for the camera
    rz_cam : np.ndarray
      5 values from the mean state vector (theta/phi/dist/pitch/yaw),
      the internal camera format of RodenZ
    view_info : ObserverIntrinsics
      resolution information
    distortion_parameters : tuple[np.ndarray, np.ndarray]
      camera intrinsics matrix and distortion coefficients
    """
    view_matrix = get_invert_x_and_z() @ get_np_viewpoint(*rz_cam[:6])
    rotation_matrix = view_matrix[:3, :3]
    translation_vector = view_matrix[:3, 3]
    rodrigues, _ = cv2.Rodrigues(rotation_matrix)

    camera_matrix = get_ndc_to_screen_space(view_info.resolution_x, view_info.resolution_y) @ get_np_ndc_cam(rz_cam[-1], view_info.resolution_x, view_info.resolution_y)

    return {
        "name": name,
        "size": [view_info.resolution_x, view_info.resolution_y],
        "matrix": camera_matrix.tolist(),
        "distortions": distortion_parameters[0].tolist(),
        "rotation": np.array(rodrigues).tolist(),
        "translation": translation_vector.tolist()
    }
