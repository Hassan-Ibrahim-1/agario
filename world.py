import random

import pygame
from food import Food
from game import utils
from hud import Hud
from player import Player
from pygame import Vector2, Color
from utils import Bounds

colors = [
    Color(255, 0, 0),  # red
    Color(0, 255, 0),  # green
    Color(0, 0, 255),  # blue
    Color(255, 255, 0),  # yellow
    Color(128, 0, 128),  # purple
    Color(255, 165, 0),  # orange
    Color(165, 42, 42),  # brown
    Color(255, 192, 203),  # pink
    Color(0, 255, 255),  # cyan
]


class Chunk:
    MAX_FOOD_PER_CHUNK = 100
    FOOD_ATTRACTION = 5
    FOOD_ATTRACTION_RADIUS = 20

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

        if (
            px >= self.position.x
            and px <= self.position.x + self.width
            and py >= self.position.y
            and py <= self.position.y + self.height
        ):
            return True

        return False

    # returns a point in the chunk
    def random_pos(self) -> Vector2:
        return Vector2(
            random.randint(int(self.position.x), int(self.position.x + self.width)),
            random.randint(int(self.position.y), int(self.position.y + self.height)),
        )

    def update(self, screen):
        food_to_remove: list[int] = []
        collision_circles = self.player.collision_circles()
        for i, food in enumerate(self.food):
            food_eaten = False
            fcc = food.collision_circle()
            for cc in collision_circles:
                if cc.is_colliding_with(fcc):
                    self.player.size = (self.player.size**2 + food.radius**2) ** 0.5
                    food_to_remove.append(i)
                    food_eaten = True
                    break
                # check if the player is close enough to start
                # making the food be attracted to the player
                else:
                    fcc.radius = self.FOOD_ATTRACTION_RADIUS
                    if cc.is_colliding_with(fcc):
                        dir = (self.player.position - food.position).normalize()
                        food.position += dir * self.FOOD_ATTRACTION

            if not food_eaten:
                food.render(screen, self.player.camera)

        # go in reverse order to avoid skipping over elements
        for i in sorted(food_to_remove, reverse=True):
            del self.food[i]

    def spawn_food(self, n_food: int):
        if len(self.food) >= self.MAX_FOOD_PER_CHUNK:
            return

        for _ in range(n_food):
            self.food.append(
                Food(self.random_pos(), random.randint(5, 20), random.choice(colors))
            )


class World:
    CHUNKS_PER_AXIS = 9

    def __init__(self, screen, player: Player) -> None:
        self.chunks: list[Chunk] = []
        self.player = player
        self.hud = Hud(screen)

        pos = Vector2(0, 0)
        for _ in range(self.CHUNKS_PER_AXIS):
            pos.y = 0
            for _ in range(self.CHUNKS_PER_AXIS):
                self.chunks.append(Chunk(pos.copy(), player))
                self.chunks[-1].spawn_food(Chunk.MAX_FOOD_PER_CHUNK)
                pos.y += Chunk.CHUNK_SIZE
                # print(pos)

            pos.x += Chunk.CHUNK_SIZE

        for chunk in self.chunks:
            chunk.spawn_food(100)

    # renders the hud as well
    def update(self, screen):
        for chunk in self.get_render_chunks(screen):
            chunk.update(screen)
        self.hud.render(self.player)

    # get the chunk that the player is in and the 9 surrounding chunks
    # the first element is always the chunk that the player is currently in
    def get_render_chunks(self, screen) -> list[Chunk]:
        chunks = []
        for chunk in self.chunks:
            if chunk.contains_player():
                chunks.append(chunk)
                chunks += self.get_surrounding_chunks(screen)
                break

        return chunks

    def get_surrounding_chunks(self, screen) -> list[Chunk]:
        chunk_x = int(self.player.position.x // Chunk.CHUNK_SIZE)
        chunk_y = int(self.player.position.y // Chunk.CHUNK_SIZE)

        surrounding_chunks = []

        chunks_horiz = int(
            screen.get_width() // (2 * Chunk.CHUNK_SIZE * self.player.camera.zoom) + 2
        )
        chunks_vert = int(
            screen.get_height() // (2 * Chunk.CHUNK_SIZE * self.player.camera.zoom) + 2
        )
        for dx in range(-chunks_horiz + 1, chunks_horiz):
            for dy in range(-chunks_vert + 1, chunks_vert):
                neighbor_x = chunk_x + dx
                neighbor_y = chunk_y + dy

                for chunk in self.chunks:
                    chunk_grid_x = int(chunk.position.x // Chunk.CHUNK_SIZE)
                    chunk_grid_y = int(chunk.position.y // Chunk.CHUNK_SIZE)

                    if chunk_grid_x == neighbor_x and chunk_grid_y == neighbor_y:
                        surrounding_chunks.append(chunk)

        return surrounding_chunks

    def render_chunk_outlines(self, screen):
        for chunk in self.chunks:
            pos = self.player.camera.to_screen_pos(screen, chunk.position)
            rect = pygame.Rect(
                pos.x,
                pos.y,
                chunk.width * self.player.camera.zoom,
                chunk.height * self.player.camera.zoom,
            )
            # print(f"pos {pos} width {chunk.width} height {chunk.height}")
            pygame.draw.rect(
                screen,
                "green",
                rect,
                int(10.0 * self.player.camera.zoom),
                int(10.0 * self.player.camera.zoom),
            )

    def bounds(self) -> Bounds:
        s = Chunk.CHUNK_SIZE * self.CHUNKS_PER_AXIS
        return Bounds(Vector2(0, 0), s, s)
