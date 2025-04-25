import pygame
from pygame import Vector2

from player import Player


class Hud:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)

    def render(self, player: Player):
        self._draw_score(player.score())

    def _draw_score(self, score: int):
        text = self.font.render(f"Score: {int(score)}", True, "black")
        w, h = self.screen.get_size()
        self.screen.blit(
            text, Vector2(w - text.get_width() - 50, h - text.get_height() - 50)
        )
