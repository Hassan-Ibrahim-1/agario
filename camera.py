from pygame import Vector2, Surface


class Camera:
    # dumb hard coded values
    MIN_ZOOM = 0.2
    MAX_ZOOM = 5

    def __init__(self, target: Vector2, zoom: float = 1) -> None:
        self.offset = Vector2(0, 0)
        # Camera does not mutate this
        self.target = target
        self.zoom = zoom

    # only use this when rendering
    # not for stuff like physics or pathfinding
    def to_screen_pos(self, screen: Surface, pos: Vector2) -> Vector2:
        half_w = screen.get_width() // 2
        half_h = screen.get_height() // 2
        center_relative = (pos - self.target) * self.zoom
        top_left_relative = center_relative
        top_left_relative.x += half_w
        top_left_relative.y += half_h
        return top_left_relative
