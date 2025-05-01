from pygame import Vector2, Color
from collision_circle import CollisionCircle
import pygame
from food import Food
from weapon import Effect
from typing import Optional

from camera import Camera


class Enemy:
    ENEMY_DAMAGE = 10

    def __init__(
        self, pos: Vector2, size: int, color: Color, velocity: float = 15
    ) -> None:
        self.position = pos
        self.velocity = velocity
        self.color = color
        self.size = size
        self._effect: Optional[Effect] = None
        self._effect_duration = 0.0

    def render(self, screen, camera: Camera):
        screen_pos = camera.to_screen_pos(screen, self.position)
        pygame.draw.circle(screen, self.color, screen_pos, self.size * camera.zoom)

    def set_effect(self, effect: Effect):
        self._effect = effect
        self._effect_duration = effect.duration()

    def update(self, player_pos: Vector2, dt: float):
        dir = player_pos - self.position

        vel = self.velocity
        if self._effect is not None:
            if self._effect_duration <= 0:
                self._effect = None
                self._effect_duration = 0
            else:
                if self._effect == Effect.SLOW_DOWN:
                    vel *= self._effect.slowdown_factor()
                self._effect_duration -= dt

        v = dir.normalize() * vel * dt
        self.position += v

    def collision_circle(self) -> CollisionCircle:
        return CollisionCircle(self.position.copy(), self.size)

    def eat_food(self, food: Food):
        self.size = (self.size**2 + food.radius**2) ** 0.5
