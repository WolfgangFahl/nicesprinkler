'''
Created on 13.08.2024

@author: wf
'''
# sprinkler/controller.py

from sprinkler.model import SprinklerModel

class SprinklerController:
    def __init__(self, model: SprinklerModel, use_hardware: bool = False):
        self.model = model
        self.use_hardware = use_hardware
        if use_hardware:
            # Initialize hardware connections here
            pass

    def move_sprinkler(self, h_angle: float, v_angle: float):
        if self.use_hardware:
            # Send commands to actual stepper motors
            pass
        # Return the movement for simulation purposes
        return h_angle, v_angle

    def spray_water(self, duration: float):
        if self.use_hardware:
            # Activate water flow
            pass
        # Return the spray duration for simulation purposes
        return duration

    def simulate_sprinkler(self):
        spray_points = self.model.calculate_spray_points()
        movements = []
        for h_angle, v_angle, distance in spray_points:
            movement = self.move_sprinkler(h_angle, v_angle)
            spray_duration = self.spray_water(0.1)  # Spray for 0.1 seconds at each point
            movements.append((movement, spray_duration))
        return movements