import random

import pygame
from food import Food
from player import Player
from pygame import Vector2, Color

colors = [
    Color(255, 0, 0),      # red
    Color(0, 255, 0),      # green
    Color(0, 0, 255),      # blue
    Color(255, 255, 0),    # yellow
    Color(128, 0, 128),    # purple
    Color(255, 165, 0),    # orange
    Color(165, 42, 42),    # brown
    Color(255, 192, 203),  # pink
    Color(0, 255, 255)     # cyan
]


class Chunk:
    MAX_FOOD_PER_CHUNK = 100

    CHUNK_SIZE = 1000

    def __init__(self, position: Vector2, player: Player) -> None:
        # top left corner
        self.position = position
        self.width = self.CHUNK_SIZE
        self.height = self.CHUNK_SIZE
        self.food: list[Food] = []
        self.player = player

    def contains_player(self) -> bool:
        px = self.player.position.x
        py = self.player.position.y

        if px >= self.position.x and px <= self.position.x + self.width and \
           py >= self.position.y and py <= self.position.y + self.height:
            return True


        return False

    # returns a point in the chunk
    def random_pos(self) -> Vector2:
        return Vector2(random.randint(int(self.position.x), int(self.position.x + self.width)),
                       random.randint(int(self.position.y), int(self.position.y + self.height)))

    def update(self, screen):
        self.render_food(screen)

    def spawn_food(self, n_food: int):
        if (len(self.food) >= self.MAX_FOOD_PER_CHUNK):
            return

        for _ in range(n_food):
            self.food.append(Food(self.random_pos(),
                                 random.randint(5, 20),
                                 random.choice(colors)))
    def render_food(self, screen):
        for food in self.food:
            food.render(screen, self.player.position)

class World:
    WORLD_WIDTH = 6000
    WORLD_HEIGHT = 6000

    # despawn food when not in chunk
    def __init__(self, player: Player) -> None:
        self.chunks: list[Chunk] = []
        self.player = player

        chunks_per_axis = 3

        pos = Vector2(0, 0)
        for _ in range(chunks_per_axis):
            pos.y = 0
            for _ in range(chunks_per_axis):
                self.chunks.append(Chunk(pos.copy(), player))
                self.chunks[-1].spawn_food(Chunk.MAX_FOOD_PER_CHUNK)
                pos.y += Chunk.CHUNK_SIZE
                print(pos)

            pos.x += Chunk.CHUNK_SIZE

        for chunk in self.chunks:
            chunk.spawn_food(100)

    def update(self, screen):
        for chunk in self.chunks:
            if chunk.contains_player():
                chunk.update(screen)

    def render_chunk_outlines(self, screen, player: Player):
        for chunk in self.chunks:
            pos = player.camera.to_screen_pos(screen, chunk.position)
            rect = pygame.Rect(pos.x, pos.y, chunk.width, chunk.height)
            # print(f"pos {pos} width {chunk.width} height {chunk.height}")
            pygame.draw.rect(screen, "green", rect, 10, 10)
