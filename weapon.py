import math
import pygame
from enum import Enum
from pygame import Vector2

from food import Camera
from texture import Texture


class Effect(Enum):
    SLOW_DOWN = 0


class Weapon:
    def __init__(
        self,
        pos: Vector2,
        effect: Effect,
        fire_rate: float,
        texture: Texture,
    ) -> None:
        self.position = pos
        self.effect = effect
        self.fire_rate = fire_rate
        self.texture = texture

    def look_at(self, screen, camera: Camera, target_position: Vector2):
        pos = camera.to_screen_pos(screen, self.position)
        direction = target_position - pos
        self.texture.rotation = direction.angle_to(pygame.Vector2(1, 0))

    def render(self, screen, camera: Camera):
        self.texture.render(
            screen,
            camera.to_screen_pos(screen, self.position),
            camera.zoom,
        )
