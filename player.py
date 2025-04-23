import pygame
from pygame import Color, Surface, Vector2
from pygame.key import ScancodeWrapper
import time, math, random

from bar import Bar
from camera import Camera
from collision_circle import CollisionCircle


class Blob:
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
        self.dir = Vector2(0, 0)

    def update(self, size: int, speed: Vector2, dt: float):
        self.size = size
        self.position += speed * dt

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
    MAX_SPEED = 200
    MAX_HEALTH = 100
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

        self.blobs: list[Blob] = [
            Blob(
                self.position.copy(),
                self.size,
                self.color,
                self.camera,
            )
        ]

    def update(self, keys: ScancodeWrapper, dt: float):
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
                self.split()

        # clamp values
        if self.speed.x > self.MAX_SPEED:
            self.speed.x = self.MAX_SPEED
        if self.speed.y > self.MAX_SPEED:
            self.speed.y = self.MAX_SPEED
        if self.speed.x < -self.MAX_SPEED:
            self.speed.x = -self.MAX_SPEED
        if self.speed.y < -self.MAX_SPEED:
            self.speed.y = -self.MAX_SPEED

        if not moving:
            self.speed = Vector2(0, 0)

        for blob in self.blobs:
            blob.update(self.size, self.speed, dt)

        self.position += self.speed * dt

    def _spawn_blobs(self):
        blobs = []
        positions = self._generate_circle_positions(
            self.blob_count, self.size, self.position
        )
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

    def food_eaten_callback(self):
        self._spawn_blobs()

    def split(self):
        if self.size <= self.MIN_SIZE:
            self.size = self.MIN_SIZE
            return

        # if _spawn_blobs fails these are used to reset state
        original_size = self.size
        original_blob_count = self.blob_count

        self.blob_count *= 2
        self.size = self.size // 2

        # this is garbage
        try:
            self._spawn_blobs()
        except:
            self.size = original_size
            self.blob_count = original_blob_count
            pass

    def _generate_circle_positions(
        self,
        num_circles,
        radius,
        center: Vector2,
        max_attempts=10000,
    ) -> list[Vector2]:
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

                # Check for overlap with existing circles
                if all(
                    math.hypot(x - px, y - py) >= diameter for (px, py) in positions
                ):
                    positions.append(new_pos)
                    break
            else:
                raise Exception("Could not place all circles without overlap.")

        return positions

    def render(self, screen: Surface):
        for blob in self.blobs:
            blob.render(screen)
        # pygame.draw.circle(
        #     screen,
        #     self.color,
        #     self.camera.to_screen_pos(screen, self.position),
        #     self.size * self.camera.zoom,
        # )

    def render_bar(self, screen: Surface):
        self.bar.render(screen, self.health / self.MAX_HEALTH)

    # returns a list of collision circles of all player blobs
    def collision_circles(self) -> list[CollisionCircle]:
        circles = []
        for blob in self.blobs:
            circles.append(blob.collision_circle())

        return circles
