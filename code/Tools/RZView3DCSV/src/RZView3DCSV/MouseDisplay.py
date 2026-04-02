from RZVisuals import BaseDisplay, Camera, Observer, DisplayConfig

import numpy as np

class MouseDisplay(BaseDisplay):
    def __init__(self, config: DisplayConfig):
        super().__init__(config)
        self.renderer.loadColorModeShaders()
        self.camera = Camera(1.0)

    def draw(self, balls: list[np.ndarray] = [], skele: list[list[int]] = []) -> bool:
        """
        balls: a list of np.array with shape 3, (x,y,z)
        skele: a list of connections, every entry is a list of indices that are connected
        """        
        for s in skele:
            if s[0] >= len(balls) or s[1] >= len(balls):
                continue
            self.renderer.drawConnection(balls[s[0]], balls[s[1]])
        for b in balls:
            self.renderer.drawBall(b, (0, 0, 0))

