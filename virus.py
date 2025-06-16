from pygame import Vector2, Color
from collision_circle import CollisionCircle
import pygame
from food import Food
from player import Blob
import math

from camera import Camera


class Virus:
    def __init__(self, pos: Vector2, size: int) -> None:
        self.position = pos
        self.size = size

    def render(self, screen, camera: Camera):
        screen_pos = camera.to_screen_pos(screen, self.position)
        center_x, center_y = screen_pos
        radius = self.size * camera.zoom

        # Spiky shape parameters
        num_spikes = 12
        inner_radius = radius * 0.7
        outer_radius = radius * 1.3

        points = []
        for i in range(num_spikes * 2):
            angle = math.pi * i / num_spikes
            r = outer_radius if i % 2 == 0 else inner_radius
            x = center_x + math.cos(angle) * r
            y = center_y + math.sin(angle) * r
            points.append((x, y))

        # Draw spiky shape
        pygame.draw.polygon(screen, Color(0, 255, 0), points)

        # Optional: draw central circle on top
        pygame.draw.circle(screen, Color(0, 180, 0), screen_pos, inner_radius)

    def collision_circle(self) -> CollisionCircle:
        return CollisionCircle(self.position.copy(), self.size)
