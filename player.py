import pygame
from pygame import Color, Surface, Vector2
from pygame.key import ScancodeWrapper
import time, math, random
from weapon import Weapon
from typing import Optional
from utils import Bounds

import utils

from bar import Bar
from camera import Camera
from collision_circle import CollisionCircle


class Blob:
    COHESION_STRENGTH = 20

    def __init__(
        self,
        pos: Vector2,
        size: int,
        color: pygame.Color,
        camera: Camera,
    ):
        self.position = pos
        self.size = size
        self.color = color
        self.camera = camera

    def update(
        self,
        size: int,
        speed: Vector2,
        dt: float,
        blobs: list["Blob"],
        center_of_mass: Vector2,
    ):
        self.size = size
        speed += self._cohesion_force(center_of_mass)
        self.position += speed * dt

        for other in blobs:
            if other is self:
                continue

            delta = self.position - other.position
            dist = delta.length()
            min_dist = self.size + other.size

            if dist < min_dist and dist > 0:
                overlap = min_dist - dist
                push_dir = delta.normalize()

                self.position += push_dir * (overlap / 2)
                other.position -= push_dir * (overlap / 2)

    def _cohesion_force(self, center_of_mass: Vector2) -> Vector2:
        if center_of_mass == self.position:
            return Vector2(0, 0)
        return (center_of_mass - self.position).normalize() * self.COHESION_STRENGTH

    def render(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            self.camera.to_screen_pos(screen, self.position),
            self.size * self.camera.zoom,
        )

    def collision_circle(self) -> CollisionCircle:
        return CollisionCircle(self.position.copy(), self.size)


class Player:
    STARTING_SIZE = 40
    MIN_SIZE = 10
    MAX_SPEED = 2000
    MAX_HEALTH = 100
    MAX_SIZE = 70
    MAX_BLOBS = 5
    # in ms
    SPLIT_COOLDOWN = 0.5

    def __init__(self, pos: Vector2, color: Color) -> None:
        self.speed = Vector2(0, 0)
        self.position = pos
        self.size: int = self.STARTING_SIZE
        self.acceleration: int = 500
        self.color = color
        self.health = self.MAX_HEALTH
        self.bar = Bar(Vector2(100, 100), Color(0, 0, 0), Color(255, 0, 0), 100, 20)
        self.growth_rate = 1
        self.blob_count = 1
        self.last_split: float = 0
        self.camera = Camera(self.position)
        self.weapon: Weapon | None = None
        # place holder value
        self.bounds = Bounds(Vector2(0, 0), 0, 0)

        self.blobs: list[Blob] = [
            Blob(
                self.position.copy(),
                self.size,
                self.color,
                self.camera,
            )
        ]

    def update(self, screen, keys: ScancodeWrapper, dt: float):
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

        if keys[pygame.K_SPACE]:
            current_time = time.time()
            if self.last_split + self.SPLIT_COOLDOWN < current_time:
                self.last_split = current_time
                self._split()

        # clamp values
        max_speed = self.MAX_SPEED / (self.size**0.5)
        if self.speed.x > max_speed:
            self.speed.x = max_speed
        if self.speed.y > max_speed:
            self.speed.y = max_speed
        if self.speed.x < -max_speed:
            self.speed.x = -max_speed
        if self.speed.y < -max_speed:
            self.speed.y = -max_speed

        if not moving:
            self.speed = Vector2(0, 0)

        center_of_mass = self._calculate_center_of_mass()
        for blob in self.blobs:
            blob.update(self.size, self.speed.copy(), dt, self.blobs, center_of_mass)

        self.position += self.speed * dt

        if self.weapon is not None:
            if self.weapon.ammo <= 0:
                self.weapon = None
            else:
                self._update_weapon(screen, dt)

    def _calculate_center_of_mass(self) -> Vector2:
        center = Vector2(0, 0)
        for blob in self.blobs:
            center += blob.position

        return center / len(self.blobs)

    def _update_weapon(self, screen, dt: float):
        assert self.weapon is not None
        if pygame.mouse.get_pressed()[0]:
            pos = self.camera.to_screen_pos(screen, self.position)
            self.weapon.spawn_bullet(utils.direction_to(pos, utils.mouse_pos()))

        self.weapon.update(self.bounds, dt)

    def _render_weapon(self, screen):
        assert self.weapon is not None
        self.weapon.position = self.position
        self.weapon.look_at(screen, self.camera, utils.mouse_pos())
        self.weapon.texture.rotation += 180
        self.weapon.render(screen, self.camera)

    def _spawn_blobs(self) -> bool:
        blobs = []
        positions = self._generate_blob_positions(
            self.blob_count, self.size, self.position
        )

        if positions is None:
            return False

        for i in range(self.blob_count):
            blobs.append(
                Blob(
                    positions[i].copy(),
                    self.size,
                    self.color,
                    self.camera,
                )
            )
        self.blobs = blobs
        return True

    def _split(self):
        if self.size <= self.MIN_SIZE:
            self.size = self.MIN_SIZE
            return

        # if _spawn_blobs fails these are used to reset state
        original_size = self.size
        original_blob_count = self.blob_count

        if self.blob_count == self.MAX_BLOBS:
            return

        self.blob_count += 1
        self.blob_count = int(pygame.math.clamp(self.blob_count, 1, self.MAX_BLOBS))

        self.size = self.size // 2
        self.size = int(pygame.math.clamp(self.size, self.MIN_SIZE, self.MAX_SIZE))

        if not self._spawn_blobs():
            self.size = original_size
            self.blob_count = original_blob_count

    def _generate_blob_positions(
        self,
        num_circles,
        radius,
        center: Vector2,
        max_attempts=10000,
    ) -> Optional[list[Vector2]]:
        area_size = math.sqrt(num_circles) * 3 * radius
        cx, cy = center
        half_size = area_size / 2
        diameter = 2 * radius
        positions: list[Vector2] = []

        for _ in range(num_circles):
            for _ in range(max_attempts):
                x = random.uniform(cx - half_size + radius, cx + half_size - radius)
                y = random.uniform(cy - half_size + radius, cy + half_size - radius)
                new_pos = Vector2(x, y)

                if all(
                    math.hypot(x - px, y - py) >= diameter for (px, py) in positions
                ):
                    positions.append(new_pos)
                    break
            else:
                return None

        return positions

    def render(self, screen: Surface):
        for blob in self.blobs:
            blob.render(screen)

        if self.weapon is not None:
            self._render_weapon(screen)

    def render_bar(self, screen: Surface):
        self.bar.render(screen, self.health / self.MAX_HEALTH)

    # returns a list of collision circles of all player blobs
    def collision_circles(self) -> list[CollisionCircle]:
        circles = []
        for blob in self.blobs:
            circles.append(blob.collision_circle())

        return circles

    # TODO: fix this calculation
    # maybe have a dedicated variable
    def score(self) -> int:
        size = self.size * self.blob_count
        return size - self.STARTING_SIZE
