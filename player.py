import pygame
from pygame import Color, Surface, Vector2
from pygame.key import ScancodeWrapper
from camera import Camera
import random


class Player:
    STARTING_SIZE = 40
    MAX_SPEED = 200

    def __init__(self, pos: Vector2, color: Color) -> None:
        self.speed = Vector2(0, 0)
        self.position = pos
        self.size: int = self.STARTING_SIZE
        self.acceleration: int = 500
        self.color = color

        self.camera = Camera(self.position)
        self.blobs = [  # Store multiple blobs
            {
            "position": pos,
            "speed": Vector2(0, 0),
                "size": self.STARTING_SIZE,
            }
        ]

        self.camera = Camera(pos)



    # returns if the player is moving or not
    def update(self, keys: ScancodeWrapper, dt: float) -> bool:
        moving = False
        direction = Vector2(0, 0)
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
            self.split()

        if direction.length() > 0:
            direction = direction.normalize()

        for blob in self.blobs:
            blob["speed"] = direction * self.acceleration * dt
            blob["position"] += blob["speed"] * dt

        return moving

    def split(self):
        new_blobs = []
        for blob in self.blobs:
            if blob["size"] > 20:  # Ensure it doesn't get too small
                blob["size"] //= 2
                offset = Vector2(random.randint(-20, 20), random.randint(-20, 20))
                new_blobs.append(
                    {
                        "position": blob["position"] + offset,
                        "speed": blob["speed"] * 2,  # Eject with some force
                        "size": blob["size"],
                    }
                )
        self.blobs.extend(new_blobs)

    def get_center(self) -> Vector2:
        return sum((blob["position"] for blob in self.blobs), Vector2()) / len(self.blobs)

    def blob_render(self, screen: Surface):
        self.camera.update_offset(screen)
        for blob in self.blobs:
            screen_pos = blob["position"] - self.camera.offset
            pygame.draw.circle(screen, self.color, (int(screen_pos.x), int(screen_pos.y)), blob["size"])


        # clamp values
        if self.speed.x > self.MAX_SPEED:
            self.speed.x = self.MAX_SPEED
        if self.speed.y > self.MAX_SPEED:
            self.speed.y = self.MAX_SPEED
        if self.speed.x < -self.MAX_SPEED:
            self.speed.x = -self.MAX_SPEED
        if self.speed.y < -self.MAX_SPEED:
            self.speed.y = -self.MAX_SPEED

    # only use this when rendering
    # not for stuff like physics or pathfinding
    def get_screen_pos(self, screen: Surface) -> Vector2:
        self.camera.update_offset(screen)
        return self.position - self.camera.offset

    def render(self, screen: Surface):
        print(f"screen pos: {self.get_screen_pos(screen)}")
        pygame.draw.circle(screen, self.color, self.get_screen_pos(screen), self.size)
        self.blob_render(screen)

