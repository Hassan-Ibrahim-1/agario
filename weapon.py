import pygame, time
from enum import Enum
from pygame import Vector2

from pygame import Color
from camera import Camera
from collision_circle import CollisionCircle
import utils
from texture import Texture
from timer import Timer


class Effect(Enum):
    SLOW_DOWN = 0

    # how long in seconds the effect lasts for
    def duration(self) -> float:
        if self == Effect.SLOW_DOWN:
            return 0.5
        else:
            return 0

    # meant to be applied to speed
    def slowdown_factor(self) -> float:
        assert self == Effect.SLOW_DOWN
        return 0.5


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
        ammo: int,
        texture: Texture,
    ) -> None:
        self.position = pos
        self.effect = effect
        self.fire_rate = fire_rate
        self.texture = texture
        self.bullets: list[Bullet] = []
        self.bullet_speed = 800
        self.ammo = ammo
        self._timer = Timer()
        self._first_shot = True

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
            self.delete_bullet(i)

    def spawn_bullet(self, dir: Vector2):
        if self.ammo <= 0:
            return

        time_threshold = 1.0 / self.fire_rate
        if self._timer.elapsed() > time_threshold or self._first_shot:
            self._first_shot = False
            self._timer.reset()
        else:
            return

        self.ammo -= 1
        self.bullets.append(
            Bullet(
                self.position.copy(),
                self.bullet_speed * dir,
                Color(252, 186, 3),
            )
        )

    # returns an index of the first enemy that bullet collides with
    # also deletes the bullet that collides with that enemy
    def check_collision(
        self,
        collision_circles: list[CollisionCircle],
    ) -> int | None:
        for i, cc in enumerate(collision_circles):
            for j, bullet in enumerate(self.bullets):
                if bullet.collision_circle().is_colliding_with(cc):
                    self.delete_bullet(j)
                    return i
        return None

    def delete_bullet(self, i: int):
        del self.bullets[i]
