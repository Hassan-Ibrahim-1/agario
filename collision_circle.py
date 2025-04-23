from pygame import Vector2


class CollisionCircle:
    def __init__(self, position: Vector2, radius: int) -> None:
        self.position = position
        self.radius = radius

    def is_colliding_with(self, other: "CollisionCircle") -> bool:
        distance = self.position.distance_to(other.position)
        return distance <= (self.radius + other.radius)
