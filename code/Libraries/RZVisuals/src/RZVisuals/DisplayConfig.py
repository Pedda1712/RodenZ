from dataclasses import dataclass

@dataclass
class DisplayConfig:
    dimensions: tuple[int, int] = (1280, 960)
    clear_color: tuple[float, float, float, float] = (0.2, 0.2, 0.2, 1.0)
    fov: float = 45
