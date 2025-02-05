import pygame
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

mylist = ["red", "green", "blue", "yellow", "purple", "orange", "brown", "pink", "cyan"]
random_colour = random.choice(mylist)

# Constants
WIDTH, HEIGHT = 800, 600
FOOD_RADIUS = 5
FOOD_COLOR = (0, 255, 0)  # Green food
FOOD_COUNT = 50  # Number of food particles

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
food_particles = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(FOOD_COUNT)]

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    pygame.draw.circle(screen, random_colour, player_pos, 40)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

   
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.


    def spawn_food():
        # Spawns a new food particle at a random location.
        return (random.randint(0, WIDTH), random.randint(0, HEIGHT))

    
    # Event handling
   
    
    # Draw food particles
    for food in food_particles:
        pygame.draw.circle(screen, FOOD_COLOR, food, FOOD_RADIUS)
    dt = clock.tick(60) / 1000
    
    pygame.display.flip()  # Update display



pygame.quit()

