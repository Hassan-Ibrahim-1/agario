import random
import pygame
from pygame import Vector2, Color
from enemy import Enemy
from food import Food
from player import Player
import utils
from world import World

pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SCALED, vsync=1
)
clock = pygame.time.Clock()
running = True
dt = 0
zoom = 1

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

font = pygame.font.SysFont(None, 24)
img = font.render("Hello World", True, "blue")

ENEMY_DAMAGE = 10

player = Player(
    Vector2(screen.get_width() / 2, screen.get_height() / 2),
    random.choice(colors),
)

world = World(player)


def random_world_pos() -> Vector2:
    return Vector2(
        random.randint(0, World.WORLD_WIDTH),
        random.randint(0, World.WORLD_HEIGHT),
    )


def spawn_food() -> Food:
    return Food(
        random_world_pos(),
        random.randint(5, 20),
        random.choice(colors),
    )


enemies: list[Enemy] = []
for x in range(10):
    xpos = random.randint(0, SCREEN_WIDTH)
    ypos = random.randint(0, SCREEN_HEIGHT)
    enemies.append(
        Enemy(
            Vector2(xpos, ypos),
            random.randint(20, 80),
            random.choice(colors),
        )
    )


def dist(p1, p2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    xd = x2 - x1
    yd = y2 - y1
    return (xd**2 + yd**2) ** 0.5


# TODO: there's too much happening the game loop
# split stuff up

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.MOUSEWHEEL:
            player.camera.zoom += event.y * 0.05
            player.camera.zoom = pygame.math.clamp(
                player.camera.zoom,
                player.camera.MIN_ZOOM,
                player.camera.MAX_ZOOM,
            )

        elif event.type == pygame.QUIT:
            running = False

    screen.fill("white")

    player.render(screen)

    world.update(screen)

    collision_circles = player.collision_circles()
    enemies_to_remove: set[int] = set()
    for i, enemy in enumerate(enemies):
        for cc in collision_circles:
            if cc.is_colliding_with(enemy.collision_circle()):
                if enemy.size < player.size:
                    player.size = (player.size**2 + enemy.size**2) ** 0.5
                    enemies_to_remove.add(i)
                else:
                    player.health -= ENEMY_DAMAGE
                    print("taking damage")
                break

    for i in sorted(enemies_to_remove, reverse=True):
        del enemies[i]

    for enemy in enemies:
        enemy.render(screen, player.camera)
        enemy.update(player.position, dt)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        running = False

    player.update(keys, dt)

    player.render_bar(screen)
    world.render_chunk_outlines(screen, player)

    # print(player.camera.zoom)

    pygame.display.flip()

pygame.quit()
