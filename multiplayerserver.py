import asyncio
import websockets
import json
import uuid

players = {}
sockets = {}

players_lock = asyncio.Lock()


async def broadcast_game_state():
    broadcast_interval = 1/60

    while True:
        await asyncio.sleep(broadcast_interval)

        async with players_lock:
            if not players:
                continue

            game_state_to_broadcast = players.copy()

            current_sockets = list(sockets.keys())

        game_state_json = json.dumps(game_state_to_broadcast)

        await asyncio.gather(
            *[ws.send(game_state_json)
              for ws in current_sockets],
            return_exceptions=True
        )


async def handler(websocket):
    player_id = str(uuid.uuid4())
    await websocket.send(player_id)

    async with players_lock:
        players[player_id] = {"x": 0, "y": 0, "health": 100, "id": player_id}
        sockets[websocket] = player_id

    print(f"Player connected: {player_id}. Total players: {len(players)}")

    try:
        async for message in websocket:
            data = json.loads(message)

            if isinstance(data, dict) and "id" in data and "x" in data and "y" in data:
                async with players_lock:
                    if data["id"] in players:
                        players[data["id"]]["x"] = data["x"]
                        players[data["id"]]["y"] = data["y"]

    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed by client: {player_id}")
    except Exception as e:
        print(f"Error in handler for player {player_id}: {e}")
    finally:
        print(f"Cleaning up state for player {player_id}...")
        async with players_lock:
            if websocket in sockets:
                del players[sockets[websocket]]
                del sockets[websocket]
                print(
                    f"Player {player_id} removed from shared state. Total players remaining: {len(players)}")


async def main():
    print("Starting server...")

    start_server = websockets.serve(handler, "localhost", 8765)

    broadcast_task = asyncio.create_task(broadcast_game_state())

    print("Server is running on ws://localhost:8765")
    await asyncio.gather(start_server, broadcast_task)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped by user.")
