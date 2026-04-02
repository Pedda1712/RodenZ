from dataclasses import dataclass

@dataclass
class Observer:
    camera_dist: float = 25
    camera_pitch: float = 0
    camera_yaw: float = 0
    camera_fov: float = 45
    camera_fine_pitch: float = 0
    camera_fine_yaw: float = 0
    camera_fine_roll: float = 0

@dataclass
class ObserverIntrinsics:
    resolution_x: int
    resolution_y: int
    sync_skip: int
