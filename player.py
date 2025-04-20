import pygame
from pygame import Color, Surface, Vector2
from pygame.key import ScancodeWrapper
import time

from bar import Bar
from camera import Camera


class Blob:
    def __init__(
        self,
        target_pos: Vector2,
        size: int,
        speed: Vector2,
        color: pygame.Color,
        camera: Camera,
    ):
        self.target_position = target_pos
        self.size = size
        self.speed = speed
        self.color = color
        self.camera = camera

    def render(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            self.camera.to_screen_pos(screen, self.target_position),
            self.size * self.camera.zoom,
        )


class Player:
    STARTING_SIZE = 40
    MAX_SPEED = 200
    MAX_HEALTH = 100
    # in ms
    SPLIT_COOLDOWN = 1000

    def __init__(self, pos: Vector2, color: Color) -> None:
        self.speed = Vector2(0, 0)
        self.position = pos
        self.size: int = self.STARTING_SIZE
        self.acceleration: int = 500
        self.color = color
        self.health = self.MAX_HEALTH
        self.bar = Bar(Vector2(100, 100), Color(0, 0, 0), Color(255, 0, 0), 100, 20)
        self.growth_rate = 1
        self.last_split: float = 0
        self.camera = Camera(self.position)

        self.blobs: list[Blob] = [
            Blob(
                self.position,
                self.size,
                self.speed,
                self.color,
                self.camera,
            )
        ]

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

        return moving

    def split(self):
        blob_count = len(self.blobs) * 2

        print("spawning new blobs")
        print(f"current len: {len(self.blobs)}")
        print(f"new len: {blob_count}")

        self.blobs = []
        for _ in range(blob_count):
            self.blobs.append(
                Blob(
                    self.position,
                    self.size,
                    self.speed,
                    self.color,
                    self.camera,
                )
            )

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
