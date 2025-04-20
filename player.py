import pygame
from pygame import Color, Surface, Vector2
from pygame.key import ScancodeWrapper
import time, math

from bar import Bar
from camera import Camera


class Blob:
    def __init__(
        self,
        pos: Vector2,
        size: int,
        color: pygame.Color,
        camera: Camera,
    ):
        self.position = pos.copy()
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


class Player:
    STARTING_SIZE = 40
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
                self.position,
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

        self.spawn_blobs()

        for blob in self.blobs:
            blob.update(self.size, self.speed, dt)

        self.position += self.speed * dt

    def spawn_blobs(self):
        self.blobs = []
        positions = self.generate_circle_positions(
            self.blob_count, self.size, self.position
        )
        for i in range(self.blob_count):
            self.blobs.append(
                Blob(
                    positions[i],
                    self.size,
                    self.color,
                    self.camera,
                )
            )

    def split(self):
        self.blob_count *= 2
        self.size = self.size // 2

        print("spawning new blobs")
        print(f"current len: {len(self.blobs)}")
        print(f"new len: {self.blob_count}")

    def generate_circle_positions(self, num_circles, radius, center):
        positions: list[Vector2] = []
        diameter = 2 * radius
        grid_size = math.ceil(math.sqrt(num_circles))

        total_grid_size = grid_size * diameter
        x0 = center[0] - total_grid_size / 2 + radius
        y0 = center[1] - total_grid_size / 2 + radius

        count = 0
        for i in range(grid_size):
            for j in range(grid_size):
                if count >= num_circles:
                    break
                x = x0 + i * diameter
                y = y0 + j * diameter
                positions.append(Vector2(x, y))
                count += 1

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
