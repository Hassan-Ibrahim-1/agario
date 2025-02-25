from pygame import Vector2, Surface

class Camera:
    def __init__(self, target: Vector2) -> None:
        self.offset = Vector2(0, 0)
        # Camera does not mutate this
        self.target = target

    def update_offset(self, screen: Surface) -> None:
        half_w = screen.get_width() // 2
        half_h = screen.get_height() // 2
        self.offset.x = self.target.x - half_w
        self.offset.y = self.target.y - half_h

    # only use this when rendering
    # not for stuff like physics or pathfinding
    def to_screen_pos(self, screen: Surface, pos: Vector2) -> Vector2:
        self.update_offset(screen)
        return pos - self.offset
