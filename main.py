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

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    pygame.draw.circle(screen, random_colour, player_pos, 40)
    screen.blit(img, pygame.Vector2(player_pos.x - img.get_width() / 2, player_pos.y - img.get_height() / 2))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt
    if keys[pygame.K_ESCAPE]:
        running = False

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
