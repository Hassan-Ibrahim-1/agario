import random

import pygame
from food import Food
from hud import Hud
from player import Player
from camera import Camera
from pygame import Vector2, Color
from utils import Bounds
from weapon import Weapon
from enemy import Enemy

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
        self._player = player
        self._weapons: list[Weapon] = []

    def contains_player(self) -> bool:
        px = self._player.position.x
        py = self._player.position.y

        return (
            px >= self.position.x
            and px <= self.position.x + self.width
            and py >= self.position.y
            and py <= self.position.y + self.height
        )

    # returns a point in the chunk
    def random_pos(self) -> Vector2:
        return Vector2(
            random.randint(int(self.position.x), int(
                self.position.x + self.width)),
            random.randint(int(self.position.y), int(
                self.position.y + self.height)),
        )

    def update(self, screen, enemies: list[Enemy], respawn=False):
        food_to_remove: list[int] = []
        player_collision_circles = self._player.collision_circles()
        enemy_collision_circles = [enemy.collision_circle()
                                   for enemy in enemies]
        for i, food in enumerate(self.food):
            food_eaten = False
            fcc = food.collision_circle()
            for j, cc in enumerate(player_collision_circles):
                if cc.is_colliding_with(fcc):
                    # self._player.size = (self._player.size**2 + food.radius**2) ** 0.5
                    self._player.blobs[j].eat_food(food)
                    food_to_remove.append(i)
                    food_eaten = True
                    break
                # check if the player is close enough to start
                # making the food be attracted to the player
                else:
                    fcc.radius = self.FOOD_ATTRACTION_RADIUS
                    if cc.is_colliding_with(fcc):
                        dir = (self._player.position -
                               food.position).normalize()
                        food.position += dir * self.FOOD_ATTRACTION

            for j, cc in enumerate(enemy_collision_circles):
                if i in food_to_remove:
                    continue

                if cc.is_colliding_with(fcc):
                    enemies[j].eat_food(food)
                    food_to_remove.append(i)
                    food_eaten = True
                    break

            if not food_eaten:
                food.render(screen, self._player.camera)

        if self._player.weapon is None and self._player.can_pickup_weapon:
            weapon_picked_up = False
            for i, weapon in enumerate(self._weapons):
                for cc in player_collision_circles:
                    if cc.is_colliding_with(weapon.collision_circle()):
                        self._player.weapon = self._weapons.pop(i)
                        weapon_picked_up = True
                        break

                if weapon_picked_up:
                    break

        # go in reverse order to avoid skipping over elements
        for i in sorted(food_to_remove, reverse=True):
            del self.food[i]

        if respawn and len(self.food) < self.MAX_FOOD_PER_CHUNK:
            self.food.append(
                Food(
                    self.random_pos(),
                    random.randint(5, 20),
                    random.choice(colors),
                )
            )

    def render_weapons(self, screen, camera: Camera):
        for weapon in self._weapons:
            weapon.render(screen, camera)

    def add_weapon(self, weapon: Weapon):
        self._weapons.append(weapon)

    def spawn_food(self, n_food: int):
        if len(self.food) >= self.MAX_FOOD_PER_CHUNK:
            return

        for _ in range(n_food):
            self.food.append(
                Food(
                    self.random_pos(),
                    random.randint(5, 20),
                    random.choice(colors),
                )
            )


class World:
    CHUNKS_PER_AXIS = 9
    FOOD_RESPAWN_TIME = 60

    def __init__(self, screen, player: Player) -> None:
        self.chunks: list[Chunk] = []
        self.player = player
        self.hud = Hud(screen)
        self.time = 0

        pos = Vector2(0, 0)
        for _ in range(self.CHUNKS_PER_AXIS):
            pos.y = 0
            for _ in range(self.CHUNKS_PER_AXIS):
                self.chunks.append(Chunk(pos.copy(), player))
                self.chunks[-1].spawn_food(Chunk.MAX_FOOD_PER_CHUNK)
                pos.y += Chunk.CHUNK_SIZE

            pos.x += Chunk.CHUNK_SIZE

        for chunk in self.chunks:
            chunk.spawn_food(100)

    # renders the hud as well
    def update(self, screen, enemies: list[Enemy]):
        self.time += 1
        respawn = (self.time % self.FOOD_RESPAWN_TIME == 0)
        for chunk in self.get_render_chunks(screen):
            chunk.update(screen, enemies, respawn)
            chunk.render_weapons(screen, self.player.camera)
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

    # returns width, height
    def size(self) -> tuple[int, int]:
        s = self.CHUNKS_PER_AXIS * Chunk.CHUNK_SIZE
        return s, s

    def random_chunk(self) -> Chunk:
        return random.choice(self.chunks)
