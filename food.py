from pygame import Color, Vector2
import pygame
from camera import Camera


class Food:
    def __init__(self, pos: Vector2, radius: int, color: Color) -> None:
        self.position = pos
        self.radius = radius
        self.color = color

    def render(self, screen, camera: Camera):
        # screen_pos = self.position - player_position + pygame.Vector2(
        #     screen.get_width() / 2,
        #     screen.get_height() / 2
        # )
        screen_pos = camera.to_screen_pos(screen, self.position)

        pygame.draw.circle(
            screen,
            self.color,
            (int(screen_pos.x), int(screen_pos.y)),
            self.radius * camera.zoom,
        )
