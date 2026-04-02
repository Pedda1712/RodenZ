from RZVisuals import BaseDisplay, Camera, Observer, DisplayConfig

import numpy as np
from PIL import Image

class CameraExtrinsicsToolDisplay(BaseDisplay):
    def __init__(self, config: DisplayConfig, texfilename: str, initial_position: Observer):
        super().__init__(config)
        img = Image.open(texfilename)
        img_data = np.array(list(img.getdata()), np.uint8)
        self.renderer.loadTextureModeShaders()
        self.renderer.loadTexture(img_data, img.size[0], img.size[1])
        self.camera = Camera(0.1)
        self.camera.observer = initial_position

    def draw(self, world_dims: tuple[int, int, int]) -> bool:
        self.renderer.drawBackWalls(world_dims)
