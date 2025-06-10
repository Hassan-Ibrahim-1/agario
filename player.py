import pygame
from pygame import Color, Surface, Vector2
from pygame.key import ScancodeWrapper
import time, math, random
from weapon import Weapon
from typing import Optional, Callable
from utils import Bounds
from food import Food

import utils

from camera import Camera
from collision_circle import CollisionCircle


class Blob:
    COHESION_STRENGTH = 20
    MIN_SIZE = 10
    MAX_SIZE = 70

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
        speed: Vector2,
        dt: float,
        blobs: list["Blob"],
        center_of_mass: Vector2,
    ):
        speed += self._cohesion_force(center_of_mass)
        self.position += speed * dt
        self.position.x = min(max(self.position.x,0),9000)
        self.position.y = min(max(self.position.y,0),9000)

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

    def eat_food(self, food: Food):
        self.size = (self.size**2 + food.radius**2) ** 0.5

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

    # returns two new child blobs
    def split(self) -> Optional[tuple["Blob", "Blob"]]:
        if self.size <= self.MIN_SIZE:
            self.size = self.MIN_SIZE
            return None

        # if _spawn_blobs fails these are used to reset state
        original_size = self.size

        self.size = self.size // 2
        self.size = int(pygame.math.clamp(self.size, self.MIN_SIZE, self.MAX_SIZE))

        res = self._spawn_blobs()
        if res is None:
            self.size = original_size
        return res

    def _spawn_blobs(self) -> Optional[tuple["Blob", "Blob"]]:
        positions = self._generate_blob_positions(
            2,
            self.size,
            self.position,
        )

        if positions is None:
            return None

        children = (
            Blob(
                positions[0].copy(),
                self.size,
                self.color,
                self.camera,
            ),
            Blob(
                positions[1].copy(),
                self.size,
                self.color,
                self.camera,
            ),
        )
        return children

    def _generate_blob_positions(
        self,
        num_circles,
        radius,
        center: Vector2,
        max_attempts=100000,
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

    def collision_circle(self) -> CollisionCircle:
        return CollisionCircle(self.position.copy(), self.size)


class Player:
    STARTING_SIZE = 40
    MAX_SPEED = 2000
    MAX_HEALTH = 100
    # should be an even number
    MAX_BLOBS = 6
    # in ms
    SPLIT_COOLDOWN = 0.5
    SMALLEST_BLOB_REABSORBTION_TIME = 3600

    def __init__(self, pos: Vector2, color: Color) -> None:
        self.speed = Vector2(0, 0)
        self.position = pos
        self.size: int = self.STARTING_SIZE
        self.acceleration: int = 500
        self.color = color
        self.growth_rate = 1
        self.last_split: float = 0
        self.camera = Camera(self.position)
        self.weapon: Optional[Weapon] = None
        self.smallest_blob = 0
        self.smallest_blob_timer = 0
        # place holder value
        self.bounds = Bounds(Vector2(0, 0), 0, 0)
        # hacky way of communicating to World that the key
        # required to pick up a weapon is pressed
        self.can_pickup_weapon = False
        self.weapon_discard_callback: Optional[Callable[[Weapon], None]] = None

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

        if self.weapon is None:
            self.can_pickup_weapon = keys[pygame.K_e]

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
            
        # REABSORBTION
        new_smallest = 0
        current_min_size = math.inf
        for i in range(len(self.blobs)):
            if self.blobs[i].size < current_min_size:
                new_smallest = i
                current_min_size = self.blobs[i].size
        if new_smallest == self.smallest_blob and len(self.blobs) > 1:
            self.smallest_blob_timer += 1
        else:
            self.smallest_blob_timer = 0
            self.smallest_blob = new_smallest
        
        if self.smallest_blob_timer > self.SMALLEST_BLOB_REABSORBTION_TIME:
            self.blobs[(self.smallest_blob + 1) % len(self.blobs)].size += self.blobs[self.smallest_blob].size
            self.blobs.pop(self.smallest_blob)

        self.size = 0
        for blob in self.blobs:
           self.size += blob.size 

        scaled_speed = self.speed * (self.STARTING_SIZE / self.size)**0.5

        center_of_mass = self._calculate_center_of_mass()
        self.position.x = center_of_mass.x
        self.position.y = center_of_mass.y
        
        for blob in self.blobs:
            blob.update(scaled_speed, dt, self.blobs, center_of_mass)
        
        if self.weapon is not None:
            if self.weapon.ammo <= 0:
                assert self.weapon_discard_callback is not None
                self.weapon_discard_callback(self.weapon.copy())
                self.weapon = None
            else:
                self._update_weapon(screen, dt)

    def _calculate_center_of_mass(self) -> Vector2:
        center = Vector2(0, 0)
        for blob in self.blobs:
            center += blob.size * blob.position

        return center / self.size

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

    def _split(self):
        if len(self.blobs) >= self.MAX_BLOBS: return
        new_blobs: list[Blob] = []
        for blob in self.blobs:
            new_blob_count = len(new_blobs)
            if new_blob_count + 3 > self.MAX_BLOBS:
                new_blobs.append(blob)
            else:
                children = blob.split()
                if children is not None:
                    new_blobs.append(children[0])
                    new_blobs.append(children[1])
                else:
                    new_blobs.append(blob)
        self.blobs = new_blobs

    def render(self, screen: Surface):
        for blob in self.blobs:
            blob.render(screen)

        if self.weapon is not None:
            self._render_weapon(screen)

    # returns a list of collision circles of all player blobs
    def collision_circles(self) -> list[CollisionCircle]:
        circles = []
        for blob in self.blobs:
            circles.append(blob.collision_circle())

        return circles

    def score(self) -> int:
        size = 0
        for b in self.blobs:
            size += b.size
        return size - self.STARTING_SIZE
