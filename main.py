import pygame
from pygame import Vector2, Color
from enemy import Enemy
from player import Player

# pygame setup
pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0

import random

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

font = pygame.font.SysFont(None, 24)
img = font.render('hello', True, "blue")

# Constants
WORLD_WIDTH, WORLD_HEIGHT = 6000, 6000  # Large world size
FOOD_RADIUS = 5
FOOD_COLOR = (0, 255, 0)  # Green food
FOOD_COUNT = 100  # Number of food particles
PLAYER_SPEED = 300  # Pixels per second
STARTING_SIZE = 40  # Initial player size

player = Player(
    Vector2(
        screen.get_width() / 2,
        screen.get_height() / 2
    ),
    random.choice(colors)
)

food_particles = [(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)) for _ in range(FOOD_COUNT)]

enemies: list[Enemy] = [] 
for x in range(10):
    xpos = random.randint(0, SCREEN_WIDTH)
    ypos = random.randint(0, SCREEN_HEIGHT)
    enemies.append(Enemy(Vector2(xpos, ypos), random.choice(colors)))


def spawn_food():
    # Spawns a new food particle at a random location.
    return (random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT))

while running:
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # raw food (world space, stays in place)
    for food in food_particles:
        food_screen_pos = food - player.position + pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        pygame.draw.circle(screen, FOOD_COLOR, (int(food_screen_pos.x), int(food_screen_pos.y)), FOOD_RADIUS)

    pygame.draw.circle(screen, player.color, player.position, 40)
    screen.blit(img, pygame.Vector2(player.position.x - img.get_width() / 2, player.position.y - img.get_height() / 2))


    for enemy in enemies:
        enemy.render(screen, player.position)
        enemy.update(player.position, dt)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        running = False

    moving = player.update(keys, dt)
    if not moving:
        player.speed = pygame.Vector2(0, 0)

    # d = v / t
    player.position += player.speed * dt

    # Check for food collision
    new_food_particles = []
    for food in food_particles:
        distance = (player.position - pygame.Vector2(food)).length()
        if distance < player.size:  # Collision detected
            player.size += 1  # Grow the player
            new_food_particles.append(spawn_food())  # Respawn food
        else:
            new_food_particles.append(food)

    food_particles = new_food_particles  # Update food list

    # flip() the display to put your work on screen
    pygame.display.flip()

pygame.quit()
