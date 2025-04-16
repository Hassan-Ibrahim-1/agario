import asyncio
import websockets #import ts in replit to run the code
import json

#store players (player_id -> player data)
players = {}

async def handle_player(websocket, path):
    player_id = str(websocket.remote_address)  
    players[player_id] = {"x": 0, "y": 0, "health": 100}  

    try:
        while True:
            message = await websocket.recv() 
            data = json.loads(message)  

            # Update player position
            if "x" in data and "y" in data:
                players[player_id]["x"] = data["x"]
                players[player_id]["y"] = data["y"]

            # Broadcast game state to all connected players
            game_state = json.dumps(players)  
            await websocket.send(game_state)  

    except websockets.exceptions.ConnectionClosed:
        # Remove player from the game state when they disconnect
        del players[player_id]

async def main():
    
    async with websockets.serve(handle_player, "localhost", 8765):
        await asyncio.Future()  # Run server forever

asyncio.run(main())

#FOR REPLIT