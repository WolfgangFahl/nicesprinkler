'''
Created on 2024-08-13

@author: wf
'''
import math
from nicegui import ui
from sprinkler.sprinkler_core import SprinklerSystem

class SprinklerSimulation:
    """
    A sprinkler simulation
    """
    def __init__(self, sprinkler_system: SprinklerSystem):
        self.sprinkler_system = sprinkler_system

    def add_lawn0(self):
        # Add lawn
        lawn_width = self.sprinkler_system.config.lawn.width
        lawn_length = self.sprinkler_system.config.lawn.length
        with self.scene.group().move(y=-0.01):  # Slightly below zero to avoid z-fighting with the grid
            self.scene.box(lawn_width, 0.02, lawn_length).material('#7CFC00')  # Lawn green


    def add_lawn(self):
        # Add lawn with correct orientation
        self.lawn_width = self.sprinkler_system.config.lawn.width
        self.lawn_length = self.sprinkler_system.config.lawn.length
        with self.scene.group().move(y=0):  # Move to ground level
            self.scene.box(self.lawn_width, self.lawn_length, 0.02).material('#7CFC00')  # Lawn green

    def move_camera(self):
        self.scene.move_camera(
            x=self.lawn_width/2,
            y=-self.lawn_length/2,
            z=self.self.lawn_length/2,
            look_at_x=self.lawn_width/2,
            look_at_y=self.lawn_length/2,
            look_at_z=0
        )

    def setup_scene(self):
        """
        setup the scene
        """
        self.scene = ui.scene(
            width=1600,
            height=900,
            grid=True,
            background_color='#87CEEB'  # Sky blue
        ).classes('w-full h-[900px]')
        self.add_lawn()

        # Add sprinkler
        sprinkler_pos = self.sprinkler_system.config.sprinkler_position
        with self.scene.group().move(x=sprinkler_pos.x, y=sprinkler_pos.y, z=sprinkler_pos.z):
            self.scene.cylinder(0.1, 0.1, 0.5).material('#808080')  # Grey cylinder for sprinkler base
            self.sprinkler_head = self.scene.sphere(0.05).material('#4682B4').move(z=0.5)  # Steel blue sphere for sprinkler head

        # Load and position the STL model
        sprinkler_pos = self.sprinkler_system.config.sprinkler_position
        with self.scene.group().move(x=sprinkler_pos.x, y=sprinkler_pos.y, z=sprinkler_pos.z):
            self.sprinkler_model = self.scene.stl('./sprinkler.stl').material('#808080')  # Grey color
            self.sprinkler_model.scale(0.01)  # Adjust scale as needed

        self.move_camera()

    def simulate_sprinkler(self):
        spray_points = self.sprinkler_system.calculate_spray_points()

        for h_angle, v_angle, distance in spray_points:
            # Move sprinkler head
            self.sprinkler_head.move(z=0.5)  # Reset to original position
            self.sprinkler_head.rotate(h_angle, 0, v_angle)

            # Show water spray
            sprinkler_pos = self.sprinkler_system.config.sprinkler_position
            end_x = sprinkler_pos.x + distance * math.cos(math.radians(h_angle))
            end_y = sprinkler_pos.y + distance * math.sin(math.radians(h_angle))
            end_z = sprinkler_pos.z + distance * math.tan(math.radians(v_angle))

            self.scene.line([sprinkler_pos.x, sprinkler_pos.y, sprinkler_pos.z + 0.5],
                            [end_x, end_y, end_z]).material('#1E90FF', opacity=0.5)  # Light blue, semi-transparent

            ui.timer(0.1, lambda: None)  # Small delay to visualize movement
