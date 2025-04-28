import pygame
from pygame import Vector2


def mouse_pos() -> Vector2:
    x, y = pygame.mouse.get_pos()
    return Vector2(x, y)


def mul_vec(vec1: Vector2, vec2: Vector2) -> Vector2:
    return Vector2(vec1.x * vec2.x, vec1.y * vec2.y)


def direction_to(p: pygame.Vector2, target: pygame.Vector2) -> pygame.Vector2:
    direction = target - p
    return direction.normalize()
