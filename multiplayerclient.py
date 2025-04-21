import asyncio
import websockets
import json
import pygame

pygame.init()
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

async def game_loop(player, players):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player["y"] -= 5
    if keys[pygame.K_s]:
        player["y"] += 5
    if keys[pygame.K_a]:
        player["x"] -= 5
    if keys[pygame.K_d]:
        player["x"] += 5

    screen.fill((255, 255, 255))

    for p in players.values():
        pygame.draw.circle(screen, (255, 0, 0), (p["x"], p["y"]), 20)

    pygame.draw.circle(screen, (0, 255, 0), (player["x"], player["y"]), 20)

    pygame.display.flip()

async def receive_game_state(websocket, player, players):
    while True:
        try:
            msg = await websocket.recv()
            incoming = json.loads(msg)
            players.update(incoming)
            if player["id"] in players:
                del players[player["id"]]
        except Exception as e:
            print(f"Error receiving game state: {e}")
            break

async def send_player_updates(websocket, player):
    while True:
        try:
            await websocket.send(json.dumps(player))
            await asyncio.sleep(1/60)
        except Exception as e:
            print(f"Error sending player updates: {e}")
            break

async def run_game():
    players = {}
    player = {"x": SCREEN_WIDTH // 2, "y": SCREEN_HEIGHT // 2, "id": None}
    
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("Connected to server")
        player["id"] = await websocket.recv()
        print("Player ID:", player["id"])

        recv_task = asyncio.create_task(receive_game_state(websocket, player, players))
        send_task = asyncio.create_task(send_player_updates(websocket, player))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            await game_loop(player, players)
            await asyncio.sleep(1/60)

        recv_task.cancel()
        send_task.cancel()
        await asyncio.gather(recv_task, send_task, return_exceptions=True)

    pygame.quit()

asyncio.run(run_game())