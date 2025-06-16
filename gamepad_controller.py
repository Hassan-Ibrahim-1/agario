import pygame
from pygame import Vector2
from typing import Optional, Tuple


class JoystickController:

    
    def __init__(self):
        self.joystick: Optional[pygame.joystick.Joystick] = None 
        self.deadzone = 0.1  # Deadzone for analog sticks
        self.connected = False
        self._init_joystick()
    
    def _init_joystick(self):
        
        pygame.joystick.init()
        
      
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init() 
            self.connected = True
            print(f"Controller connected: {self.joystick.get_name()}")
        else:
            print("No controller detected")
    
    def get_movement_vector(self) -> Vector2:
      
        if not self.connected or self.joystick is None:
            return Vector2(0, 0)
        
  
        x_axis = self.joystick.get_axis(0)  
        y_axis = self.joystick.get_axis(1)  
        
        # Apply deadzone
        if abs(x_axis) < self.deadzone:
            x_axis = 0
        if abs(y_axis) < self.deadzone:
            y_axis = 0
        
 
        return Vector2(x_axis, -y_axis)
    
    def is_split_pressed(self) -> bool:

        if not self.connected or self.joystick is None:
            return False
        
       
        return self.joystick.get_button(5)
    
    def is_weapon_pickup_pressed(self) -> bool:
 
        if not self.connected or self.joystick is None:
            return False
        
       
        return self.joystick.get_button(4)
    
    def is_weapon_discard_pressed(self) -> bool:
   
        if not self.connected or self.joystick is None:
            return False
        
      
        return self.joystick.get_button(3)
    
    def get_controller_info(self) -> str:
     
        if not self.connected or self.joystick is None:
            return "No controller connected"
        
        return f"Controller: {self.joystick.get_name()}, Axes: {self.joystick.get_numaxes()}, Buttons: {self.joystick.get_numbuttons()}"
    
    def is_connected(self) -> bool:
        """Check if a controller is connected."""
        return self.connected
    
    def update(self):
    
        pass


# Button mapping for Logitech F310:
# Button 0: A (NOT USED)
# Button 1: B (NOT USED)
# Button 2: X (NOT USED)
# Button 3: Y DROP WEAPON
# Button 4: Left Bumper WEAPON PICKUP
# Button 5: Right Bumper SPLIT
# Button 6: Back (NOT USED)
# Button 7: Start (NOT USED)    
# Button 8: Left Stick Press (NOT USED) 
# Button 9: Right Stick Press (NOT USED)

# Axes:
# Axis 0: Left Stick X (MOVE LEFT/RIGHT)    
# Axis 1: Left Stick Y (MOVE UP/DOWN)
# Axis 2: Right Stick X (NOT USED)
# Axis 3: Right Stick Y (NOT USED)
# Axis 4: Left Trigger (NOT USED)
# Axis 5: Right Trigger (NOT USED)
# make sure to invert the y axis <<<<<<