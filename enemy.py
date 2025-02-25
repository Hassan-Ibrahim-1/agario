from pygame import Vector2, Color
import pygame

from camera import Camera

class Enemy:
    def __init__(self, pos: Vector2, color: Color, velocity: float = 15) -> None:
        self.position = pos
        self.velocity: float = velocity
        self.color = color

    def render(self, screen, camera: Camera):
        screen_pos = camera.to_screen_pos(screen, self.position)
        pygame.draw.circle(screen, self.color, screen_pos, 40)

    def update(self, player_pos: Vector2, dt: float):
        dir = player_pos - self.position
        v = dir.normalize() * self.velocity * dt
        self.position += v


    @staticmethod
    def mul_vec(vec1: Vector2, vec2: Vector2) -> Vector2:
        return Vector2(vec1.x * vec2.x, vec1.y * vec2.y)
