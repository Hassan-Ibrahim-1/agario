import pygame
from pygame import Vector2

from player import Player
from gamepad_controller import JoystickController


class Hud:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)

    def render(self, player: Player, controller: JoystickController = None, side: str = 'left'):
        self._draw_score(player.score(), side)
        if player.weapon is not None:
            self._draw_ammo(player.weapon.ammo, side)
        
        if controller:
            self._draw_controller_status(controller)

    def _draw_score(self, score: int, side: str = 'left'):
        text = self.font.render(f"Score: {int(score)}", True, "black")
        w, h = self.screen.get_size()
        if side == 'left':
            pos = Vector2(20, 20)
        else:
            pos = Vector2(w - text.get_width() - 20, 20)
        self.screen.blit(text, pos)

    def _draw_ammo(self, ammo: int, side: str = 'left'):
        text = self.font.render(f"Ammo: {ammo}", True, "black")
        w, h = self.screen.get_size()
        if side == 'left':
            pos = Vector2(20, 60)
        else:
            pos = Vector2(w - text.get_width() - 20, 60)
        self.screen.blit(text, pos)
    
    def _draw_controller_status(self, controller: JoystickController):
        if controller.is_connected():
            text = self.font.render("Controller: Connected", True, "green")
        else:
            text = self.font.render("Controller: Disconnected", True, "red")
        
        w, h = self.screen.get_size()
        self.screen.blit(text, Vector2(10, 10))
