import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

import random

mylist = ["red", "green", "blue", "yellow", "purple", "orange", "brown", "pink", "cyan"]
random_colour = random.choice(mylist)

font = pygame.font.SysFont(None, 24)
img = font.render('hello', True, "blue")

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player_speed = pygame.Vector2(0, 0)

ACCELERATION = 500
MAX_SPEED = 200

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

	pygame.draw.circle(screen, random_colour, player_pos, 40)
	screen.blit(img, pygame.Vector2(player_pos.x - img.get_width() / 2, player_pos.y - img.get_height() / 2))



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
