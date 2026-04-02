import pygame
from pygame.locals import *

from .Observer import Observer
from .DisplayConfig import DisplayConfig
from .Camera import Camera
from .Renderer import Renderer

import numpy as np

class BaseDisplay():

    def __init__(self, config: DisplayConfig):
        self.config = config
        self.clock = pygame.time.Clock()
        pygame.init()
        pygame.display.set_mode(self.config.dimensions, DOUBLEBUF|OPENGL)
        self.renderer = Renderer(self.config)
        self.camera = Camera()

    def draw(self):
        # Override this method in child implementation.
        raise RuntimeError("BaseDisplay is not supposed to be used by itself")
        
    def display(self, *args, **kwargs) -> bool:
        self.dt = self.clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            
        keys = pygame.key.get_pressed()
        self.camera.update(keys, self.dt)

        self.renderer.beginPass()
        self.renderer.setObserver(self.camera.observer)

        self.draw(*args, **kwargs)
        
        self.renderer.endPass()

        pygame.display.flip()
        pygame.time.wait(10)
        return True

    def get_last_delta(self):
        return self.dt
