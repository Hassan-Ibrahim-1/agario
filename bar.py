from pygame import Rect, Color, Vector2
import pygame

class Bar:
    def __init__(
        self,
        position: Vector2,
        base_colour: Color,
        bar_colour: Color,
        max_width: float,
        height: float
    ):
        self.base_colour = base_colour,
        self.bar_colour = bar_colour
        self.position = position
        self.max_width = max_width
        self.height = height

    def render(self, screen: pygame.Surface, bar_percent: float):
        base_rect = pygame.Rect(self.position.x,
                           self.position.y,
                           self.max_width,
                           self.height)
        pygame.draw.rect(screen, self.base_colour, base_rect)

        bar_rect = base_rect.copy()
        bar_rect.width = int(self.max_width * bar_percent)
        pygame.draw.rect(screen, self.bar_colour, bar_rect)
