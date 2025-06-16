import pygame
import random
from pygame import Vector2, Color
from enemy import Enemy
from virus import Virus
from menu import Menu
from player import Player
from texture import Texture
from weapon import Effect, Weapon
from world import World
from gamepad_controller import JoystickController
from hud import Hud
from typing import Optional
import time


class Weapons:
    def __init__(self):
        self.glock = Weapon(
            Vector2(0, 0),
            Effect.SLOW_DOWN,
            4,
            8,
            Texture("textures/gun.webp"),
        )
        self.glock.texture.scale = Vector2(0.1, 0.1)

        self.raygun = Weapon(
            Vector2(0, 0),
            Effect.DAMAGE,
            1,
            4,
            Texture("textures/raygunpng.webp"),
        )
        self.raygun.texture.scale = Vector2(0.25, 0.25)

        self.bazzoka = Weapon(
            Vector2(0, 0),
            Effect.ANNIHILATION,
            3,
            2,
            Texture("textures/bazookapng.webp"),
        )
        self.bazzoka.texture.scale = Vector2(0.6, 0.6)
        self.bazzoka.radius = 12
        self.bazzoka.bullet_speed = 600

    def as_list(self) -> list[Weapon]:
        return [
            self.glock, self.raygun, self.bazzoka
        ]

    def find_equivalent_weapon(self, other: Weapon) -> Optional[Weapon]:
        for weapon in self.as_list():
            if self._weapon_mostly_equals(weapon, other):
                return weapon
        return None

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
        
        self.controller = JoystickController()

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
        self._reset()
        self.GameOverTexture = Texture("textures/GameOver.png")

    def _reset(self):
        self.zoom: float = 1
        world_size = 9000
        left_start = Vector2(world_size * 0.25, world_size * 0.5)
        right_start = Vector2(world_size * 0.75, world_size * 0.5)
        self.player_keyboard = Player(left_start, random.choice(self.colors))
        self.player_controller = Player(right_start, random.choice(self.colors))
        self.player_keyboard.weapon_discard_callback = self._weapon_discard_callback_keyboard
        self.player_controller.weapon_discard_callback = self._weapon_discard_callback_controller

        self.world = World(self.screen, self.player_keyboard, self.controller)
        self.player_keyboard.bounds = self.world.bounds()
        self.player_controller.bounds = self.world.bounds()

        self.enemies = self._spawn_enemies()
        self.viruses = self._spawn_viruses()
        self.running = False
        self.keys: pygame.key.ScancodeWrapper

        self.weapons = Weapons()
        self._spawn_weapons()

        self.in_menu = True
        center = Vector2(
            self.screen.get_width() // 2,
            self.screen.get_height() // 2,
        )
        self.menu = Menu(self.font, center)

        self.hud_keyboard = Hud(self.screen)
        self.hud_controller = Hud(self.screen)

        self.running = True

    def _init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            flags=pygame.SCALED,
            vsync=1,
        )
        self.clock = pygame.time.Clock()

    def run(self):
        while self.running:
            self._start_frame()

            if self.in_menu:
                self._update_menu()
            else:
                self._update()

            self._end_frame()

    def _update_menu(self):
        self.menu.update()

        for button in self.menu.buttons:
            if button.is_pressed():
                if button.name == "play":
                    self.in_menu = False

                if button.name == "quit":
                    self.running = False

                return
        self.menu.render(self.screen)

    def _start_frame(self):
        self.dt = self.clock.tick(60) / 1000
        self._handle_events()
        self.controller.update()
        self.screen.fill("white")

    def _end_frame(self):
        pygame.display.flip()

    def _update(self):
        half_w = self.SCREEN_WIDTH // 2
        h = self.SCREEN_HEIGHT
        left_surface = self.screen.subsurface((0, 0, half_w, h))
        right_surface = self.screen.subsurface((half_w, 0, half_w, h))

        self.player_keyboard.update(left_surface, self.keys, self.dt, controller=None, use_arrow_keys=False)
        self.player_controller.update(right_surface, self.keys, self.dt, controller=self.controller, use_arrow_keys=True)

        self.world.update(left_surface, self.enemies)
        self._update_food_for_both_players()
        
        self._update_enemies_for_player(self.player_keyboard)
        self._update_enemies_for_player(self.player_controller)

        self.world.render_food(left_surface, self.player_keyboard.camera, self.player_keyboard)
        self.world.render_food(right_surface, self.player_controller.camera, self.player_controller)

        for enemy in self.enemies:
            enemy.render(left_surface, self.player_keyboard.camera)
            enemy.render(right_surface, self.player_controller.camera)
        
        for virus in self.viruses:
            virus.render(left_surface, self.player_keyboard.camera)
            virus.render(right_surface, self.player_controller.camera)

        self.player_keyboard.render(left_surface)
        self.player_controller.render(right_surface)

        self.hud_keyboard.render(self.player_keyboard, None, side='left')
        self.hud_controller.render(self.player_controller, self.controller, side='right')

        pygame.draw.rect(self.screen, (0, 0, 0), (half_w - 2, 0, 4, h))

        for player in [self.player_keyboard, self.player_controller]:
            player.camera.zoom = min(max(
                player.camera.zoom,
                player.camera.MIN_ZOOM * player.STARTING_SIZE / player.size),
                player.camera.MAX_ZOOM * player.STARTING_SIZE / player.size
            )

        self._player_vs_player_eat()

        if len(self.player_keyboard.blobs) <= 0 or len(self.player_controller.blobs) <= 0:
            self._reset()
            return

    def _spawn_weapons(self):
        for weapon in self.weapons.as_list():
            self._spawn_weapon(weapon.copy())

    def _spawn_weapon(self, weapon: Weapon):
        chunk = self.world.random_chunk()
        weapon.position = chunk.random_pos()
        chunk.add_weapon(weapon)

    def _weapon_discard_callback_keyboard(self, weapon: Weapon):
        base_weapon = self.weapons.find_equivalent_weapon(weapon)
        assert base_weapon is not None
        base_weapon.position = weapon.position
        self._spawn_weapon(base_weapon.copy())

    def _weapon_discard_callback_controller(self, weapon: Weapon):
        base_weapon = self.weapons.find_equivalent_weapon(weapon)
        assert base_weapon is not None
        base_weapon.position = weapon.position
        self._spawn_weapon(base_weapon.copy())

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEWHEEL:
                self.player_keyboard.camera.zoom += event.y * 0.05
                self.player_keyboard.camera.zoom = min(max(
                    self.player_keyboard.camera.zoom,
                    self.player_keyboard.camera.MIN_ZOOM * self.player_keyboard.STARTING_SIZE / self.player_keyboard.size),
                    self.player_keyboard.camera.MAX_ZOOM * self.player_keyboard.STARTING_SIZE / self.player_keyboard.size
                )
            elif event.type == pygame.QUIT:
                self.running = False

        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_ESCAPE]:
            self.running = False

        if self.keys[pygame.K_q]:
            if self.player_keyboard.weapon is not None:
                for chunk in self.world.chunks:
                    if chunk.contains_player():
                        chunk.add_weapon(self.player_keyboard.weapon.copy())
                self.player_keyboard.weapon = None
        if self.keys[pygame.K_r] or (self.controller.is_connected() and self.controller.is_weapon_discard_pressed()):
            if self.player_controller.weapon is not None:
                for chunk in self.world.chunks:
                    if chunk.contains_player():
                        chunk.add_weapon(self.player_controller.weapon.copy())
                self.player_controller.weapon = None

    def deinit(self):
        pygame.quit()

    def _spawn_enemies(self) -> list[Enemy]:
        enemies = []
        w, h = self.world.size()
        for _ in range(50):
            xpos = random.randint(1000, w)
            ypos = random.randint(1000, h)
            enemies.append(
                Enemy(
                    Vector2(xpos, ypos),
                    random.randint(20, 80),
                    random.choice(self.colors),
                )
            )

        return enemies

    def _spawn_viruses(self) -> list[Enemy]:
        viruses = []
        w, h = self.world.size()
        for _ in range(20):
            xpos = random.randint(1000, w)
            ypos = random.randint(1000, h)
            viruses.append(
                Virus(
                    Vector2(xpos, ypos),
                    random.randint(20, 80),
                )
            )

        return viruses

    def _update_enemies_for_player(self, player: Player):
        player_collision_circles = player.collision_circles()
        enemies_to_remove: set[int] = set()
        blobs_to_remove: set[int] = set()

        for j, cc in enumerate(player_collision_circles):
            for i, virus in enumerate(self.viruses):
                if cc.is_colliding_with(virus.collision_circle()):
                    player.frames_since_last_virus = 0
                    blob = player.blobs[j]
                    diff = player.position - virus.position
                    player.speed = diff.normalize() * 20000
                    player._split()

            for i, enemy in enumerate(self.enemies):
                update_enemy = True
                if cc.is_colliding_with(enemy.collision_circle()):
                    blob = player.blobs[j]
                    if enemy.size < blob.size:
                        blob.size = (blob.size**2 + enemy.size**2) ** 0.5
                        enemies_to_remove.add(i)
                        update_enemy = False
                        w,h = self.world.size()
                        self.enemies.append(
                            Enemy(
                                Vector2(random.randint(1000, w) , random.randint(1000, h)),
                                random.randint(int(player.size // 2), int(player.size * 1.5)),
                                random.choice(self.colors),
                            )
                        )
                    else:
                        enemy.eat_blob(blob)
                        blobs_to_remove.add(j)
                    break

                if update_enemy:
                    enemy.update(player.position, self.dt)

        for i in sorted(enemies_to_remove, reverse=True):
            del self.enemies[i]

        for i in sorted(blobs_to_remove, reverse=True):
            del player.blobs[i]

    def _player_vs_player_eat(self):
        blobs1 = self.player_keyboard.blobs
        blobs2 = self.player_controller.blobs
        eaten1 = set()
        eaten2 = set()
        for i, b1 in enumerate(blobs1):
            for j, b2 in enumerate(blobs2):
                dist = (b1.position - b2.position).length()
                if dist < b1.size + b2.size:
                    if b1.size > b2.size:
                        b1.size = (b1.size**2 + b2.size**2) ** 0.5
                        eaten2.add(j)
                    elif b2.size > b1.size:
                        b2.size = (b2.size**2 + b1.size**2) ** 0.5
                        eaten1.add(i)
        for i in sorted(eaten1, reverse=True):
            del blobs1[i]
        for j in sorted(eaten2, reverse=True):
            del blobs2[j]

    def _update_food_for_both_players(self):
        chunks_to_update = set()
        
        for chunk in self.world.chunks:
            if chunk.contains_player():
                chunks_to_update.add(chunk)
                chunk_x = int(self.player_keyboard.position.x // chunk.CHUNK_SIZE)
                chunk_y = int(self.player_keyboard.position.y // chunk.CHUNK_SIZE)
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        neighbor_x = chunk_x + dx
                        neighbor_y = chunk_y + dy
                        for c in self.world.chunks:
                            c_grid_x = int(c.position.x // c.CHUNK_SIZE)
                            c_grid_y = int(c.position.y // c.CHUNK_SIZE)
                            if c_grid_x == neighbor_x and c_grid_y == neighbor_y:
                                chunks_to_update.add(c)
                break
        
        for chunk in self.world.chunks:
            if chunk.contains_player():
                chunks_to_update.add(chunk)
                chunk_x = int(self.player_controller.position.x // chunk.CHUNK_SIZE)
                chunk_y = int(self.player_controller.position.y // chunk.CHUNK_SIZE)
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        neighbor_x = chunk_x + dx
                        neighbor_y = chunk_y + dy
                        for c in self.world.chunks:
                            c_grid_x = int(c.position.x // c.CHUNK_SIZE)
                            c_grid_y = int(c.position.y // c.CHUNK_SIZE)
                            if c_grid_x == neighbor_x and c_grid_y == neighbor_y:
                                chunks_to_update.add(c)
                break
        
        for chunk in chunks_to_update:
            self._update_chunk_food(chunk)
    
    def _update_chunk_food(self, chunk):
        food_to_remove = []
        
        keyboard_circles = self.player_keyboard.collision_circles()
        for i, food in enumerate(chunk.food):
            if i in food_to_remove:
                continue
            food_circle = food.collision_circle()
            for j, cc in enumerate(keyboard_circles):
                if cc.is_colliding_with(food_circle):
                    self.player_keyboard.blobs[j].eat_food(food)
                    food_to_remove.append(i)
                    break
        
        controller_circles = self.player_controller.collision_circles()
        for i, food in enumerate(chunk.food):
            if i in food_to_remove:
                continue
            food_circle = food.collision_circle()
            for j, cc in enumerate(controller_circles):
                if cc.is_colliding_with(food_circle):
                    self.player_controller.blobs[j].eat_food(food)
                    food_to_remove.append(i)
                    break
        
        for i in sorted(food_to_remove, reverse=True):
            if i < len(chunk.food):
                del chunk.food[i]
