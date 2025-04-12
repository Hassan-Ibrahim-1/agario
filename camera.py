from pygame import Vector2, Surface

class Camera:
    def __init__(self, target: Vector2, zoom = 1) -> None:
        self.offset = Vector2(0, 0)
        # Camera does not mutate this
        self.target = target
        self.zoom = zoom

    # def update_offset(self, screen: Surface) -> None:
    #     half_w = screen.get_width() // 2
    #     half_h = screen.get_height() // 2
    #     self.offset.x = self.target.x - half_w
    #     self.offset.y = self.target.y - half_h

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