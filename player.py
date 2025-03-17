import pygame
from pygame import Color, Surface, Vector2
from pygame.key import ScancodeWrapper

from bar import Bar
from camera import Camera

class Player:
    STARTING_SIZE = 40
    MAX_SPEED = 200
    MAX_HEALTH = 100

    def __init__(self, pos: Vector2, color: Color) -> None:
        self.speed = Vector2(0, 0)
        self.position = pos
        self.size: int = self.STARTING_SIZE
        self.acceleration: int = 500
        self.color = color
        self.health = self.MAX_HEALTH
        self.bar = Bar(Vector2(100, 100), Color(0, 0, 0), Color(255, 0, 0), 100, 20)

        self.camera = Camera(self.position)

    # returns if the player is moving or not
    def update(self, keys: ScancodeWrapper, dt: float) -> bool:
        moving = False
        if keys[pygame.K_w]:
            self.speed.y -= self.acceleration * dt
            moving = True
        if keys[pygame.K_s]:
            self.speed.y += self.acceleration * dt
            moving = True
        if keys[pygame.K_a]:
            self.speed.x -= self.acceleration * dt
            moving = True
        if keys[pygame.K_d]:
            self.speed.x += self.acceleration * dt
            moving = True

        # clamp values
        if self.speed.x > self.MAX_SPEED:
            self.speed.x = self.MAX_SPEED
        if self.speed.y > self.MAX_SPEED:
            self.speed.y = self.MAX_SPEED
        if self.speed.x < -self.MAX_SPEED:
            self.speed.x = -self.MAX_SPEED
        if self.speed.y < -self.MAX_SPEED:
            self.speed.y = -self.MAX_SPEED

        return moving

    # only use this when rendering
    # not for stuff like physics or pathfinding
    def get_screen_pos(self, screen: Surface) -> Vector2:
        self.camera.update_offset(screen)
        return self.position - self.camera.offset

    def render(self, screen: Surface):
        pygame.draw.circle(screen, self.color, self.get_screen_pos(screen), self.size)

    def render_bar(self, screen: Surface):
        self.bar.render(screen, self.health / self.MAX_HEALTH)
