"""
Created on 2024-08-13

@author: wf
"""

import math
import os

from nicegui import ui

from sprinkler.sprinkler_core import SprinklerSystem


class SprinklerSimulation:
    """
    An improved sprinkler simulation
    """

    def __init__(self, sprinkler_system: SprinklerSystem):
        self.sprinkler_system = sprinkler_system
        self.lawn_width = self.sprinkler_system.config.lawn.width
        self.lawn_length = self.sprinkler_system.config.lawn.length
        self.lawn_height = 0.05
        self.cx = self.lawn_width / 2
        self.cy = self.lawn_length / 2
        self.scene = None
        self.sprinkler_head = None
        self.sprinkler_model = None

    def add_lawn(self):
        with self.scene.group().move(y=0):  # Move to ground level
            self.scene.box(
                self.lawn_width, self.lawn_length, self.lawn_height
            ).material(
                "#7CFC00"
            )  # Lawn green

    def add_garden3d(self):
        # Load and position the 3D STL model of our garden
        stl_filename = os.path.basename(self.sprinkler_system.stl_file_path)
        stl_url = f"/examples/{stl_filename}"
        self.sprinkler_model = self.scene.stl(stl_url).material("#41684A")  # Bush green

        # Position the STL model relative to the lawn
        self.sprinkler_model.move(
            x=-self.cx, y=-self.cy, z=self.lawn_height / 2
        )  # Slightly below the lawn

    def add_sprinkler(self):
        # Add a simplified sprinkler representation
        sprinkler_pos = self.sprinkler_system.config.sprinkler_position
        sprinkler_height = sprinkler_pos.z  # Use the full height from the config

        # Position the sprinkler correctly based on the config
        with self.scene.group().move(x=sprinkler_pos.x, y=sprinkler_pos.y, z=0):
            # Cylinder for the full height of the sprinkler
            self.scene.cylinder(0.1, 0.1, sprinkler_height).material(
                "#4B0082"
            )  # Indigo, for contrast

            # Sprinkler head at the top of the cylinder
            self.sprinkler_head = (
                self.scene.sphere(0.05).material("#4682B4").move(z=sprinkler_height)
            )

    def add_debug_markers(self):
        # Origin marker (red)
        self.scene.sphere(0.1).material("#FF0000").move(0, 0, 0)
        # Sprinkler position marker (blue)
        sprinkler_pos = self.sprinkler_system.config.sprinkler_position
        self.scene.sphere(0.1).material("#0000FF").move(
            sprinkler_pos.x, sprinkler_pos.y, sprinkler_pos.z
        )

    def move_camera(self):
        self.scene.move_camera(
            x=self.cx,
            y=-self.lawn_length,
            z=self.lawn_length / 2,  # Moved back and lowered
            look_at_x=self.cx,
            look_at_y=self.cy,
            look_at_z=0,
        )

    def setup_scene(self):
        """
        Setup the scene
        """
        self.scene = ui.scene(
            width=1700, height=700, grid=True, background_color="#87CEEB"  # Sky blue
        ).classes("w-full h-[700px]")

        self.add_garden3d()
        self.add_lawn()
        self.add_sprinkler()
        self.add_debug_markers()

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

            self.scene.line(
                [sprinkler_pos.x, sprinkler_pos.y, sprinkler_pos.z + 0.5],
                [end_x, end_y, end_z],
            ).material(
                "#1E90FF", opacity=0.5
            )  # Light blue, semi-transparent

            ui.timer(0.1, lambda: None)  # Small delay to visualize movement
