from pygame import Vector2
import pygame

import utils


class Texture:
    def __init__(self, path: str) -> None:
        self.data = pygame.image.load(path).convert_alpha()
        self.rotation: float = 0
        self.original_size = Vector2(self.data.get_width(), self.data.get_height())
        self.scale = Vector2(1, 1)

    def render(self, screen, pos: Vector2, zoom: float):
        tex = pygame.transform.scale(
            self.data,
            utils.mul_vec(self.original_size, self.scale * zoom),
        )
        tex = pygame.transform.rotate(tex, self.rotation)
        # Get the new rect and center it
        rect = tex.get_rect(center=pos)
        screen.blit(tex, rect.topleft)
