import math
import pygame
from enum import Enum
from pygame import Vector2

from pygame import Color
from camera import Camera
from collision_circle import CollisionCircle
from game import utils
from texture import Texture


class Effect(Enum):
    SLOW_DOWN = 0


class Bullet:
    def __init__(self, pos: Vector2, vel: Vector2, color: Color):
        self.position = pos
        self.velocity = vel
        self.radius: int = 5
        self.color = color

    def update(self, dt: float):
        self.position += self.velocity * dt

    def render(self, screen, camera: Camera):
        pygame.draw.circle(
            screen,
            self.color,
            camera.to_screen_pos(screen, self.position),
            self.radius,
        )

    def collision_circle(self) -> CollisionCircle:
        return CollisionCircle(self.position, self.radius)


class Weapon:
    def __init__(
        self,
        pos: Vector2,
        effect: Effect,
        fire_rate: float,
        texture: Texture,
    ) -> None:
        self.position = pos
        self.effect = effect
        self.fire_rate = fire_rate
        self.texture = texture
        self.bullets: list[Bullet] = []
        self.bullet_speed = 800

    def look_at(
        self,
        screen,
        camera: Camera,
        target_position: Vector2,
    ):
        pos = camera.to_screen_pos(screen, self.position)
        direction = target_position - pos
        self.texture.rotation = direction.angle_to(pygame.Vector2(1, 0))

    def render(self, screen, camera: Camera):
        self.texture.render(
            screen,
            camera.to_screen_pos(screen, self.position),
            camera.zoom,
        )

        for bullet in self.bullets:
            bullet.render(screen, camera)

    # if any bullet is not inside the bounds rect then
    # that bullet gets deleted
    def update(self, bounds: utils.Bounds, dt: float):
        bullets_to_remove: list[int] = []
        for i, bullet in enumerate(self.bullets):
            if not bounds.contains(bullet.position):
                bullets_to_remove.append(i)
                continue

            bullet.update(dt)

        # go in reverse order to avoid skipping over elements
        for i in sorted(bullets_to_remove, reverse=True):
            del self.bullets[i]

    def spawn_bullet(self, dir: Vector2):
        self.bullets.append(
            Bullet(
                self.position.copy(),
                self.bullet_speed * dir,
                Color(252, 186, 3),
            )
        )

    # returns an index of the first enemy that bullet collides with
    def check_collision(
        self,
        collision_circles: list[CollisionCircle],
    ) -> int | None:
        for i, cc in enumerate(collision_circles):
            for bullet in self.bullets:
                if bullet.collision_circle().is_colliding_with(cc):
                    return i
        return None
