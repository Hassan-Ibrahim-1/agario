import pygame
from pygame import Vector2
from enemy import Enemy

# pygame setup
pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0

import random

colors = ["red", "green", "blue", "yellow", "purple", "orange", "brown", "pink", "cyan"]
random_colour = random.choice(colors)

font = pygame.font.SysFont(None, 24)
img = font.render('hello', True, "blue")

# Constants
WORLD_WIDTH, WORLD_HEIGHT = 6000, 6000  # Large world size
FOOD_RADIUS = 5
FOOD_COLOR = (0, 255, 0)  # Green food
FOOD_COUNT = 100  # Number of food particles
PLAYER_SPEED = 300  # Pixels per second
STARTING_SIZE = 40  # Initial player size

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player_speed = pygame.Vector2(0, 0)
player_size = STARTING_SIZE
food_particles = [(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)) for _ in range(FOOD_COUNT)]

ACCELERATION = 500
MAX_SPEED = 200

enemies = []
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
		food_screen_pos = food - player_pos + pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
		pygame.draw.circle(screen, FOOD_COLOR, (int(food_screen_pos.x), int(food_screen_pos.y)), FOOD_RADIUS)

	pygame.draw.circle(screen, random_colour, player_pos, 40)
	screen.blit(img, pygame.Vector2(player_pos.x - img.get_width() / 2, player_pos.y - img.get_height() / 2))
	print(player_pos)

	# Check for food collision
	new_food_particles = []
	for food in food_particles:
		distance = (player_pos - pygame.Vector2(food)).length()
		if distance < player_size:  # Collision detected
			player_size += 1  # Grow the player
			new_food_particles.append(spawn_food())  # Respawn food
		else:
			new_food_particles.append(food)

	food_particles = new_food_particles  # Update food list

	for enemy in enemies:
		enemy.render(screen)
		enemy.update(player_pos, dt)


	moving = False
	keys = pygame.key.get_pressed()
	if keys[pygame.K_w]:
		player_speed.y -= ACCELERATION * dt
		moving = True
	if keys[pygame.K_s]:
		player_speed.y += ACCELERATION * dt
		moving = True
	if keys[pygame.K_a]:
		player_speed.x -= ACCELERATION * dt
		moving = True
	if keys[pygame.K_d]:
		player_speed.x += ACCELERATION * dt
		moving = True

	if player_speed.x > MAX_SPEED:
		player_speed.x = MAX_SPEED
	if player_speed.y > MAX_SPEED:
		player_speed.y = MAX_SPEED
	if player_speed.x < -MAX_SPEED:
		player_speed.x = -MAX_SPEED
	if player_speed.y < -MAX_SPEED:
		player_speed.y = -MAX_SPEED

	if keys[pygame.K_ESCAPE]:
		running = False

	if not moving:
		player_speed = pygame.Vector2(0, 0)

	# d = v / t
	player_pos += player_speed * dt

	# flip() the display to put your work on screen
	pygame.display.flip()

pygame.quit()
