import pygame
from pygame.locals import *
from .Observer import Observer

class Camera:
    def __init__(self, mult: float = 1):
        self.observer = Observer(75, 45, -45, 53)
        self.camera_speed = 20
        self.camera_turn_speed = 100
        self.camera_fov_speed = 5
        self.mult = mult

    def update(self, keys, dt):
        if keys[pygame.K_a]:
            self.observer.camera_yaw += self.camera_turn_speed * dt * self.mult
        if keys[pygame.K_d]:
            self.observer.camera_yaw -= self.camera_turn_speed * dt * self.mult
        if keys[pygame.K_w]:
            self.observer.camera_pitch += self.camera_turn_speed * dt * self.mult
        if keys[pygame.K_s]:
            self.observer.camera_pitch -= self.camera_turn_speed * dt * self.mult
        if keys[pygame.K_q]:
            self.observer.camera_dist -= self.camera_speed * dt * self.mult
        if keys[pygame.K_e]:
            self.observer.camera_dist += self.camera_speed * dt * self.mult
        if keys[pygame.K_k]:
            self.observer.camera_fine_pitch += self.camera_turn_speed * dt * self.mult
        if keys[pygame.K_i]:
            self.observer.camera_fine_pitch -= self.camera_turn_speed * dt * self.mult
        if keys[pygame.K_j]:
            self.observer.camera_fine_yaw -= self.camera_turn_speed * dt * self.mult
        if keys[pygame.K_l]:
            self.observer.camera_fine_yaw += self.camera_turn_speed * dt * self.mult
        if keys[pygame.K_m]:
            self.observer.camera_fov += self.camera_fov_speed * dt * self.mult
        if keys[pygame.K_n]:
            self.observer.camera_fov -= self.camera_fov_speed * dt * self.mult
