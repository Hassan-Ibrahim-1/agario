import pygame
from pygame import Vector2


class Bounds:
    def __init__(self, top_left: Vector2, w: int, h: int) -> None:
        self.top_left = top_left
        self.width = w
        self.height = h

    def contains(self, p: Vector2) -> bool:
        return (p.x > self.top_left.x and p.x < self.top_left.x + self.width) and (
            p.y > self.top_left.y and p.y < self.top_left.y + self.height
        )

    def contains_circle(self, center: Vector2, radius: int) -> bool:
        return (
            center.x - radius >= self.top_left.x
            and center.x + radius <= self.top_left.x + self.width
            and center.y - radius >= self.top_left.y
            and center.y + radius <= self.top_left.y + self.height
        )


def mouse_pos() -> Vector2:
    x, y = pygame.mouse.get_pos()
    return Vector2(x, y)


def mul_vec(vec1: Vector2, vec2: Vector2) -> Vector2:
    return Vector2(vec1.x * vec2.x, vec1.y * vec2.y)


def direction_to(p: pygame.Vector2, target: pygame.Vector2) -> pygame.Vector2:
    direction = target - p
    return direction.normalize()
