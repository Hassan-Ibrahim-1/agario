import pygame
import random
import utils
from pygame import Vector2, Color
from enemy import Enemy
from food import Food
from player import Player
from texture import Texture
from weapon import Effect, Weapon
from world import World


class Weapons:
    def __init__(self):
        self.gun = Weapon(
            Vector2(0, 0),
            Effect.SLOW_DOWN,
            10,
            2,
            Texture("textures/gun.webp"),
        )
        self.gun.texture.scale = Vector2(0.1, 0.1)

    def as_list(self) -> list[Weapon]:
        return [
            self.gun,
        ]


class Game:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

    def __init__(self) -> None:
        self._init_pygame()

        self.dt: float = 0
        self.zoom: float = 1

        self.colors = [
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

        self.font = pygame.font.SysFont(None, 24)

        self.player = Player(
            Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2),
            random.choice(self.colors),
        )

        self.world = World(self.screen, self.player)
        self.player.bounds = self.world.bounds()

        self.enemies = self._spawn_enemies()
        self.running = False
        self.keys: pygame.key.ScancodeWrapper

        self.weapons = Weapons()

        self.player.weapon = self.weapons.gun

    def _init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            flags=pygame.SCALED,
            vsync=1,
        )
        self.clock = pygame.time.Clock()

    def run(self):
        self.running = True

        while self.running:
            self._update()

    def _update(self):
        self.dt = self.clock.tick(60) / 1000
        self._handle_events()
        self.screen.fill("white")

        self.world.update(self.screen)
        self._update_weapons()
        self.player.update(self.screen, self.keys, self.dt)
        self._update_enemies()

        self.player.render(self.screen)
        self.player.render_bar(self.screen)
        self.world.render_chunk_outlines(self.screen)

        pygame.display.flip()

    def _update_weapons(self):
        ccs = [enemy.collision_circle() for enemy in self.enemies]
        enemies_to_effect: list[tuple[Effect, int]] = []
        for weapon in self.weapons.as_list():
            idx = weapon.check_collision(ccs)
            if idx is not None:
                enemies_to_effect.append((weapon.effect, idx))

        for effect, i in enemies_to_effect:
            enemy = self.enemies[i]
            enemy.set_effect(effect)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEWHEEL:
                self.player.camera.zoom += event.y * 0.05
                self.player.camera.zoom = pygame.math.clamp(
                    self.player.camera.zoom,
                    self.player.camera.MIN_ZOOM,
                    self.player.camera.MAX_ZOOM,
                )

            elif event.type == pygame.QUIT:
                self.running = False

        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_ESCAPE]:
            self.running = False

    def deinit(self):
        pygame.quit()

    def _update_enemies(self):
        collision_circles = self.player.collision_circles()
        enemies_to_remove: set[int] = set()
        for i, enemy in enumerate(self.enemies):
            update_enemy = True
            for cc in collision_circles:
                if cc.is_colliding_with(enemy.collision_circle()):
                    if enemy.size < self.player.size:
                        self.player.size = (self.player.size**2 + enemy.size**2) ** 0.5
                        enemies_to_remove.add(i)
                        update_enemy = False
                    else:
                        self.player.health -= Enemy.ENEMY_DAMAGE
                    break

            if update_enemy:
                enemy.render(self.screen, self.player.camera)
                enemy.update(self.player.position, self.dt)

        for i in sorted(enemies_to_remove, reverse=True):
            del self.enemies[i]

    def _spawn_enemies(self) -> list[Enemy]:
        enemies = []
        for _ in range(10):
            xpos = random.randint(0, self.SCREEN_WIDTH)
            ypos = random.randint(0, self.SCREEN_HEIGHT)
            enemies.append(
                Enemy(
                    Vector2(xpos, ypos),
                    random.randint(20, 80),
                    random.choice(self.colors),
                )
            )
        return enemies
