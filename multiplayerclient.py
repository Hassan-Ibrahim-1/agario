import asyncio
import websockets #go into the shell and use pip install websockets
import json
import pygame


pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


player_position = {"x": SCREEN_WIDTH // 2, "y": SCREEN_HEIGHT // 2}

async def send_player_data():
    uri = "ws://localhost:8765"  
    async with websockets.connect(uri) as websocket:
        while True:
           
            data = json.dumps(player_position)
            await websocket.send(data)

           
            game_state = await websocket.recv()
            print(game_state)  

async def game_loop():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_position["y"] -= 5
    if keys[pygame.K_s]:
        player_position["y"] += 5
    if keys[pygame.K_a]:
        player_position["x"] -= 5
    if keys[pygame.K_d]:
        player_position["x"] += 5

 
    pygame.draw.circle(screen, (255, 0, 0), (player_position["x"], player_position["y"]), 20)
    pygame.display.flip()


async def run_game():
   
    asyncio.create_task(send_player_data())

    # Main game loop
    running = True
    while running:
        screen.fill((255, 255, 255)) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        await game_loop() 
        clock.tick(60)  # Cap the frame rate at 60 FPS

    pygame.quit()

asyncio.run(run_game())  

#put ts and server.py into replit]
