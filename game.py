import pygame
import random
from pygame import Vector2, Color
from enemy import Enemy
from player import Player
from texture import Texture
from weapon import Effect, Weapon
from world import World
from typing import Optional


class Weapons:
    def __init__(self):
        self.gun = Weapon(
            Vector2(0, 0),
            Effect.SLOW_DOWN,
            4,
            10,
            Texture("textures/gun.webp"),
        )
        self.gun.texture.scale = Vector2(0.1, 0.1)

    def as_list(self) -> list[Weapon]:
        return [
            self.gun,
        ]

    def find_equivalent_weapon(self, other: Weapon) -> Optional[Weapon]:
        for weapon in self.as_list():
            if self._weapon_mostly_equals(weapon, other):
                return weapon
        return None

    # checks if a weapon is equal to another
    # based on everything except position, ammo and bullets
    def _weapon_mostly_equals(self, w1: Weapon, w2: Weapon) -> bool:
        return (
            w1.fire_rate == w2.fire_rate
            and w1.effect == w2.effect
            and w1.texture == w2.texture
            and w1.bullet_speed == w2.bullet_speed
        )


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
        self.player.weapon_discard_callback = self._weapon_discard_callback

        self.world = World(self.screen, self.player)
        self.player.bounds = self.world.bounds()

        self.enemies = self._spawn_enemies()
        self.running = False
        self.keys: pygame.key.ScancodeWrapper

        self.weapons = Weapons()
        self._spawn_weapons()

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

        # player has to be updated before world for weapon pickup reasons
        self.player.update(self.screen, self.keys, self.dt)
        self.world.update(self.screen, self.enemies)
        if self.player.weapon is not None:
            self._apply_player_weapon_effects()
        self._update_enemies()
        if len(self.player.blobs) <= 0:
            self.running = False
            print("game over")
            return

        self.player.render(self.screen)
        self.world.render_chunk_outlines(self.screen)

        pygame.display.flip()

    def _spawn_weapons(self):
        for weapon in self.weapons.as_list():
            self._spawn_weapon(weapon.copy())

    def _spawn_weapon(self, weapon: Weapon):
        chunk = self.world.random_chunk()
        weapon.position = chunk.random_pos()
        chunk.add_weapon(weapon)

    def _weapon_discard_callback(self, weapon: Weapon):
        base_weapon = self.weapons.find_equivalent_weapon(weapon)
        assert base_weapon is not None
        base_weapon.position = weapon.position
        self._spawn_weapon(base_weapon.copy())

    # applies effects to enemies if any bullet collides with them
    def _apply_player_weapon_effects(self):
        assert self.player.weapon is not None
        ccs = [enemy.collision_circle() for enemy in self.enemies]
        enemies_to_effect: list[tuple[Effect, int]] = []
        idx = self.player.weapon.check_collision(ccs)
        if idx is not None:
            enemies_to_effect.append((self.player.weapon.effect, idx))

        for effect, i in enemies_to_effect:
            self.enemies[i].set_effect(effect)

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

        if self.keys[pygame.K_q]:
            if self.player.weapon is not None:
                for chunk in self.world.chunks:
                    if chunk.contains_player():
                        chunk.add_weapon(self.player.weapon.copy())
                self.player.weapon = None

    def deinit(self):
        pygame.quit()

    def _update_enemies(self):
        player_collision_circles = self.player.collision_circles()
        enemies_to_remove: set[int] = set()
        blobs_to_remove: set[int] = set()
        for i, enemy in enumerate(self.enemies):
            update_enemy = True
            for j, cc in enumerate(player_collision_circles):
                if cc.is_colliding_with(enemy.collision_circle()):
                    blob = self.player.blobs[j]
                    if enemy.size < blob.size:
                        blob.size = (blob.size**2 + enemy.size**2) ** 0.5
                        enemies_to_remove.add(i)
                        update_enemy = False
                    else:
                        enemy.eat_blob(blob)
                        blobs_to_remove.add(j)
                    break

            if update_enemy:
                enemy.render(self.screen, self.player.camera)
                enemy.update(self.player.position, self.dt)

        for i in sorted(enemies_to_remove, reverse=True):
            del self.enemies[i]

        for i in sorted(blobs_to_remove, reverse=True):
            print(f"blob: {i}")
            del self.player.blobs[i]

    def _spawn_enemies(self) -> list[Enemy]:
        enemies = []
        w, h = self.world.size()
        for _ in range(10):
            xpos = random.randint(0, w)
            ypos = random.randint(0, h)
            enemies.append(
                Enemy(
                    Vector2(xpos, ypos),
                    random.randint(20, 80),
                    random.choice(self.colors),
                )
            )

        return enemies
