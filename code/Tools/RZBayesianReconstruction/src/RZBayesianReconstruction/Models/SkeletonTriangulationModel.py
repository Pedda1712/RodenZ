import numpy as np
import jax.numpy as jnp
import jax

from RZBayesianReconstruction.Smoother import AdditiveNormalNoiseMeasurementModel
from .Observers import Observer

"""
Measurement model for skeletal state representation.
Each state is converted into absolute positions and
projected into the camera configuration encoded in
that state to produce measurements.
"""

def jnp_rotate_y(angle_rad):
    return jnp.array([
        [jnp.cos(angle_rad), 0, jnp.sin(angle_rad), 0],
        [0, 1, 0, 0],
        [-jnp.sin(angle_rad), 0, jnp.cos(angle_rad), 0],
        [0, 0, 0, 1],
    ])
def jnp_rotate_x(angle_rad):
    return jnp.array([
        [1, 0, 0, 0],
        [0, jnp.cos(angle_rad), -jnp.sin(angle_rad), 0],
        [0, jnp.sin(angle_rad), jnp.cos(angle_rad),  0],
        [0, 0, 0, 1],
    ])
def jnp_rotate_z(angle_rad):
    return jnp.array([
        [jnp.cos(angle_rad), -jnp.sin(angle_rad), 0, 0],
        [jnp.sin(angle_rad), jnp.cos(angle_rad),  0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])
def jnp_translate_z(dist):
    return jnp.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, dist],
        [0, 0, 0, 1]
    ])
def jnp_radians(deg):
    return deg * (3.141/180)

def get_jnp_viewpoint(pitch, yaw, dist, fine_pitch, fine_yaw, fine_roll):
    mat1 = jnp_rotate_y(jnp_radians(yaw))
    mat2 = jnp_rotate_x(jnp_radians(pitch))
    mat3 = jnp_translate_z(-dist)
    mat4 = jnp_rotate_y(jnp_radians(fine_yaw))
    mat5 = jnp_rotate_x(jnp_radians(fine_pitch))
    mat6 = jnp_rotate_z(jnp_radians(fine_roll))
    return mat6 @ mat5 @ mat4 @ mat3 @ mat2 @ mat1

def get_jnp_perspective(fov_deg, aspect):
    # copied from https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
    f = 1 / jnp.tan(jnp_radians(fov_deg)/2)
    return jnp.array([
        [f/aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, -1, 0]
    ])

## construction of the measurement model from vmapping the elementary projection

# function to project one ball into one observer (the elementary function doing the work)
def project_ball_into_observer(po, t_aspect, pre_projection):
    (pitch, yaw, dist, fpitch, fyaw, froll, fov) = po
    t_view = get_jnp_viewpoint(pitch, yaw, dist, fpitch, fyaw, froll)
    t_proj = get_jnp_perspective(fov, t_aspect)
    proj_view = t_proj @ t_view
    projection = (proj_view @ pre_projection).T
    return (projection[:,0:2] / jnp.clip(projection[:,2], min=0.01).reshape(-1,1)).flatten()

# project one ball into MULTIPLE observers
_v_project_ball_into_observer = jax.vmap(project_ball_into_observer, in_axes=[0, None, None])
def v_project_ball_into_observer(po, ball, t_aspect):
    pre_projection = jnp.concat((ball.T, jnp.ones(ball.shape[0]).reshape(1,-1)))
    return _v_project_ball_into_observer(po, t_aspect, pre_projection).flatten()

# project one ball into known observer with fov
def project_ball_into_observer_with_known_extrinsics(t_view, t_aspect, fov, ball):
    pre_projection = jnp.concat((ball.T, jnp.ones(ball.shape[0]).reshape(1,-1)))
    t_proj = get_jnp_perspective(fov, t_aspect)
    proj_view = t_proj @ t_view
    projection = (proj_view @ pre_projection).T
    return (projection[:,0:2] / jnp.clip(projection[:,2], min=0.01).reshape(-1,1)).flatten()

_v_project_ball_into_observer_with_known_extrinsics = jax.vmap(project_ball_into_observer_with_known_extrinsics, in_axes=[None, None, 0, 0])
def v_project_ball_into_observer_with_known_extrinsics(t_view, t_aspect, fovs, balls):
    result = _v_project_ball_into_observer_with_known_extrinsics(t_view, t_aspect, fovs, balls)
    return result

# project MULTIPLE balls into MULTIPLE observers
_vv_project_ball_into_observer = jax.vmap(v_project_ball_into_observer, in_axes=[0,0,None])
def vv_project_ball_into_observer(observers, balls, t_proj):
    return _vv_project_ball_into_observer(observers, balls, t_proj)

@jax.jit # this is the magic sauce
def jaxxed_measurement_model(observers, balls, t_aspect, reference_fovs, reference_view):
    unknown_projections = vv_project_ball_into_observer(observers, balls, t_aspect)
    known_projections = v_project_ball_into_observer_with_known_extrinsics(reference_view, t_aspect, reference_fovs, balls)
    return jnp.hstack((known_projections, unknown_projections))

class SkeletonTriangulationModel(AdditiveNormalNoiseMeasurementModel):
    reference_viewpoint: Observer
    number_of_unknown_cameras: int
    aspect_ratio: float
    
    def __init__(self, reference_viewpoint: Observer, number_of_unknown_cameras: int, compiled_skeleton: tuple[str, str], aspect_ratio: float):
        self.reference_viewpoint = reference_viewpoint
        self.number_of_unknown_cameras = number_of_unknown_cameras
        
        code = compiled_skeleton[0].replace("np", "jnp")
        exec(code, globals())
        self.to_absolute = jax.jit(jax.vmap(eval(compiled_skeleton[1])))
        self.aspect_ratio = aspect_ratio

    def measure_without_noise(self, states) -> np.ndarray:
        parameter_count = (states.shape[1] - self.number_of_unknown_cameras * 7 - 1) // 2
        
        absolute_positions = np.array(self.to_absolute(states[:, :parameter_count]))

        # this is an array of the balls of each state sample, shape: (sample_id, ball_number, 3)
        balls = absolute_positions.reshape(states.shape[0], -1, 3)
        # this is an array of the unknown observers of each state sample, shape: (sample_id, observer_number, 6)
        observers = states[:, (parameter_count * 2 + 1):].reshape(-1, self.number_of_unknown_cameras, 7)

        t_view = get_jnp_viewpoint(self.reference_viewpoint.camera_pitch, self.reference_viewpoint.camera_yaw, self.reference_viewpoint.camera_dist, self.reference_viewpoint.camera_fine_pitch, self.reference_viewpoint.camera_fine_yaw, self.reference_viewpoint.camera_fine_roll)

        fovs = states[:, (parameter_count * 2)]

        return np.array(jaxxed_measurement_model(observers, balls, self.aspect_ratio, fovs, t_view))
    
    def measure(self, states: np.ndarray) -> np.ndarray:
        parameter_count = (states.shape[1] - self.number_of_unknown_cameras * 7 - 1) // 2
        
        absolute_positions = np.array(self.to_absolute(states[:, :parameter_count]))

        # this is an array of the balls of each state sample, shape: (sample_id, ball_number, 3)
        balls = absolute_positions.reshape(states.shape[0], -1, 3)
        # this is an array of the unknown observers of each state sample, shape: (sample_id, observer_number, 5)
        observers = states[:, (parameter_count * 2 + 1):].reshape(-1, self.number_of_unknown_cameras, 7)

        t_view = get_jnp_viewpoint(self.reference_viewpoint.camera_pitch, self.reference_viewpoint.camera_yaw, self.reference_viewpoint.camera_dist, self.reference_viewpoint.camera_fine_pitch, self.reference_viewpoint.camera_fine_yaw, self.reference_viewpoint.camera_fine_roll)

        fovs = states[:, (parameter_count * 2)]

        return np.array(jaxxed_measurement_model(observers, balls, self.aspect_ratio, fovs, t_view))
    
