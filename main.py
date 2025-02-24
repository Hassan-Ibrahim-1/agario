import pygame
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))  # Fixed resolution
clock = pygame.time.Clock()
running = True
dt = 0

# Random player color
mylist = ["red", "green", "blue", "yellow", "purple", "orange", "brown", "pink", "cyan"]
random_colour = random.choice(mylist)

# Constants
WORLD_WIDTH, WORLD_HEIGHT = 6000, 6000  # Large world size
FOOD_RADIUS = 5
FOOD_COLOR = (0, 255, 0)  # Green food
FOOD_COUNT = 100  # Number of food particles
PLAYER_SPEED = 300  # Pixels per second
STARTING_SIZE = 40  # Initial player size

# Player settings
player_pos = pygame.Vector2(WORLD_WIDTH / 2, WORLD_HEIGHT / 2)  # Player starts at the center
player_size = STARTING_SIZE

# Generate food in world space
food_particles = [(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)) for _ in range(FOOD_COUNT)]

def spawn_food():
    # Spawns a new food particle at a random location.
    return (random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT))

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= PLAYER_SPEED * dt
    if keys[pygame.K_s]:
        player_pos.y += PLAYER_SPEED * dt
    if keys[pygame.K_a]:
        player_pos.x -= PLAYER_SPEED * dt
    if keys[pygame.K_d]:
        player_pos.x += PLAYER_SPEED * dt

    # Fill screen
    screen.fill("white")

    # raw food (world space, stays in place)
    for food in food_particles:
        food_screen_pos = food - player_pos + pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        pygame.draw.circle(screen, FOOD_COLOR, (int(food_screen_pos.x), int(food_screen_pos.y)), FOOD_RADIUS)

    # Draw player (always centered)
    pygame.draw.circle(screen, random_colour, (screen.get_width() // 2, screen.get_height() // 2), player_size)

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

    # Update display
    pygame.display.flip()
    
    # Limit FPS
    dt = clock.tick(60) / 1000

pygame.quit()

