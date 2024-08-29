"""
Created on 2024-08-13

@author: wf
"""

import math
import os

from ngwidgets.scene_frame import SceneFrame
from nicegui import ui

from sprinkler.sprinkler_core import SprinklerSystem
import sprinkler


class SprinklerSimulation:
    """
    An improved sprinkler simulation
    """

    def __init__(self, solution, sprinkler_system: SprinklerSystem):
        """
        constructor
        """
        self.solution = solution
        self.sprinkler_system = sprinkler_system

        # get the lawn coordinates from the configuration
        self.lawn_width = self.sprinkler_system.config.lawn.width
        self.lawn_length = self.sprinkler_system.config.lawn.length
        self.lawn_height = 0.05

        # get the center coordinates of the lawn
        self.cx = self.lawn_width / 2
        self.cy = self.lawn_length / 2

        # prepare instance variables
        self.scene = None
        self.sprinkler_head = None
        self.sprinkler_model = None

    def add_lawn(self):
        """
        add the lawn
        """
        with self.scene.group().move(x=self.cx, y=self.cy):  # Move to ground level
            self.scene.box(
                self.lawn_width, self.lawn_length, self.lawn_height
            ).material(
                "#7CFC00"
            )  # Lawn green

    def add_garden3d(self):
        """
        add the 3D model of the garden
        """
        # Load and position the 3D STL model of our garden
        stl_filename = os.path.basename(self.sprinkler_system.stl_file_path)
        stl_url = f"/examples/{stl_filename}"
        self.garden_model = self.scene_frame.load_stl(stl_filename, stl_url, scale=1.0)

    def add_sprinkler(self):
        """
        Add a simplified sprinkler representation
        """
        sprinkler_pos = self.sprinkler_system.config.sprinkler_position
        sprinkler_height = sprinkler_pos.z  # Use the full height from the config
        print(f"sprinkler_pos: {sprinkler_pos}")

        # Position the sprinkler correctly based on the config
        with self.scene.group().move(x=sprinkler_pos.x, y=sprinkler_pos.y,z=0):
            # Cylinder with height along the z-axis
            #self.scene.cylinder(
            #    top_radius=0.1,
            #    bottom_radius=0.1,
            #    height=sprinkler_height).material("#4B0082")
            # Add a box with the same height and position as the cylinder for comparison
            self.scene.box(width=0.2, height=0.2, depth=sprinkler_height).material("#FF4500").move(z=sprinkler_height / 2)


            # Sprinkler head at the top of the cylinder
            self.sprinkler_head = (
                self.scene.sphere(0.05).material("#4682B4").move(z=sprinkler_height)
            )


    def add_debug_markers(self):
        r = 0.1
        dz = -r

        def pos(title, color, x, y, z):
            print(f"{title}: {x},{y},{z}")
            self.scene.sphere(r).material(color).move(x, y, z)

        # Origin marker (red)
        pos("Red", "#FF0000", 0, 0, dz)

        # Right front corner marker (green)
        pos("Green", "#00FF00", self.lawn_width, 0, dz)

        # Right back corner marker (blue)
        pos("Blue", "#0000FF", self.lawn_width, self.lawn_length, dz)

    def move_camera(self):
        """
        position the camera
        """
        self.scene.move_camera(
            x=self.cx,
            y=-self.lawn_length,
            z=self.lawn_length / 2,  # Moved back and lowered
            look_at_x=self.cx,
            look_at_y=self.cy,
            look_at_z=0,
        )

    def setup_scene_frame(self):
        self.scene_frame = SceneFrame(self.solution, stl_color="#41684A")  # Bush green)
        self.setup_buttons()
        self.setup_scene()

    def setup_scene(self):
        """
        Setup the scene
        """

        with ui.scene(
            width=1700, height=700, grid=True, background_color="#87CEEB"  # Sky blue
        ).classes("w-full h-[700px]") as scene:
            self.scene = scene
            self.scene_frame.scene = scene

        #self.add_garden3d()
        self.add_lawn()
        self.add_sprinkler()
        self.add_debug_markers()

        self.move_camera()

    def setup_buttons(self):
        """
        add more buttons
        """
        self.scene_frame.setup_button_row()
        with self.scene_frame.button_row:
            ui.button("Start Simulation", on_click=self.simulate_sprinkler)
            ui.button("Reset", on_click=self.reset_simulation)

    async def reset_simulation(self):
        """Resets the simulation to its initial state."""
        self.scene.clear()
        self.setup_scene()
        ui.notify("Simulation reset")

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
