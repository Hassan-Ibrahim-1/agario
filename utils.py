from pygame import Vector2


def mul_vec(vec1: Vector2, vec2: Vector2) -> Vector2:
    return Vector2(vec1.x * vec2.x, vec1.y * vec2.y)


def clamp(val: float, min: float, max: float) -> float:
    if val < min:
        return min
    if val > max:
        return max
    return val
