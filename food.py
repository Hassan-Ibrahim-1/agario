from pygame import Color, Vector2
import pygame

class Food:
    def __init__(self, pos: Vector2, radius: int, color: Color) -> None:
        self.position = pos 
        self.radius = radius
        self.color = color

    def render(self, screen, player_position: Vector2):
        screen_pos = self.position - player_position + pygame.Vector2(
            screen.get_width() / 2,
            screen.get_height() / 2
        )
        pygame.draw.circle(
            screen,
            self.color,
            (
                int(screen_pos.x),
                int(screen_pos.y)
            ),
            self.radius
        )
