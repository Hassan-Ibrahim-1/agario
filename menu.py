import pygame
from pygame import Vector2, Color, Rect, Surface
from pygame.font import Font


class MouseInfo:
    def __init__(self, mouse_pos: Vector2, pressed: bool) -> None:
        self.pos = mouse_pos
        self.pressed = pressed


class Button:
    def __init__(self, name: str, rect: Rect, color: Color, font: Font) -> None:
        self.name = name
        self.rect = rect
        self.color = color
        self.mouse_info = MouseInfo(Vector2(0, 0), False)
        self.font = font

    def update(self, mouse_info: MouseInfo):
        self.mouse_info = mouse_info

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

        text = self.font.render(self.name, True, "black")
        screen.blit(text, self._center_text(text))

    def _center_text(self, text: Surface) -> Vector2:
        w, h = text.get_size()
        x = self.rect.x + (self.rect.width - w) // 2
        y = self.rect.y + (self.rect.height - h) // 2
        return Vector2(x, y)

    def is_pressed(self) -> bool:
        return self.mouse_info.pressed and self.rect.collidepoint(
            self.mouse_info.pos.x,
            self.mouse_info.pos.y,
        )


class Menu:
    def __init__(self, font: Font, center: Vector2) -> None:
        button_w = 200
        button_x = center.x - button_w // 2
        button_color = Color(3, 165, 252)
        self.font = font
        self.title_font = pygame.font.SysFont(None, 80)
        self.buttons: list[Button] = [
            Button(
                "play",
                Rect(button_x, center.y - 200, button_w, 50),
                button_color,
                self.font,
            ),
            Button(
                "quit",
                Rect(button_x, center.y - 120, button_w, 50),
                button_color,
                self.font,
            ),
        ]

    def update(self):
        self._update_buttons()

    def _update_buttons(self):
        p = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]
        mouse_info = MouseInfo(Vector2(p[0], p[1]), pressed)
        for button in self.buttons:
            button.update(mouse_info)

    def render(self, screen):
        for button in self.buttons:
            button.render(screen)
        self._render_title_text(screen)

    def _render_title_text(self, screen):
        title = self.title_font.render("BallBiters", True, "black")
        center = Vector2(
            screen.get_width() // 2,
            screen.get_height() // 2,
        )

        x = center.x - title.get_width() // 2
        y = 40

        screen.blit(title, Vector2(x, y))
