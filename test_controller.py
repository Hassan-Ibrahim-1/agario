"""
Simple test script to verify controller integration.
This will test the JoystickController class without running the full game.
"""

import pygame
import sys
from gamepad_controller import JoystickController

def test_controller():
    """Test the controller integration."""
    print("Initializing pygame...")
    pygame.init()
    
    print("Creating controller...")
    controller = JoystickController()
    
    print(f"Controller connected: {controller.is_connected()}")
    if controller.is_connected():
        print(f"Controller info: {controller.get_controller_info()}")
    
    print("\nTesting controller input (press Ctrl+C to exit):")
    print("Move the left stick to see movement values")
    print("Press right bumper to see split input")
    print("Press left bumper to see weapon pickup input")
    print("Press Y button to see weapon discard input")
    
    try:
        while True:
            # Get controller input
            movement = controller.get_movement_vector()
            split_pressed = controller.is_split_pressed()
            pickup_pressed = controller.is_weapon_pickup_pressed()
            discard_pressed = controller.is_weapon_discard_pressed()
            
            # Print status :(
            if (movement.length() > 0 or split_pressed or 
                pickup_pressed or discard_pressed):
                print(f"\rMovement: ({movement.x:.2f}, {movement.y:.2f}) | "
                      f"Split: {split_pressed} | "
                      f"Pickup: {pickup_pressed} | "
                      f"Discard: {discard_pressed}", end="", flush=True)
            
           
            pygame.time.wait(16)  # ~60 FPS 
            
    except KeyboardInterrupt:
        print("\n\nTest completed!")
    
    pygame.quit()

if __name__ == "__main__":
    test_controller() 