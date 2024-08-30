"""
Created on 2024-08-13

@author: wf
"""

import math
import os

import numpy as np
from ngwidgets.scene_frame import SceneFrame
from nicegui import ui

from sprinkler.sprinkler_core import SprinklerSystem


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
        self.init_control_values()

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
        with self.scene.group().move(x=sprinkler_pos.x, y=sprinkler_pos.y, z=0):
            # Cylinder with height along the z-axis
            # self.scene.cylinder(
            #    top_radius=0.1,
            #    bottom_radius=0.1,
            #    height=sprinkler_height).material("#4B0082")
            # Add a box with the same height and position as the cylinder for comparison
            self.scene.box(width=0.2, height=0.2, depth=sprinkler_height).material(
                "#FF4500"
            ).move(z=sprinkler_height / 2)

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
            y=-self.lawn_length * 0.4,
            z=self.lawn_length / 2,  # Moved back and lowered
            look_at_x=self.cx,
            look_at_y=self.cy,
            look_at_z=0,
        )

    def setup_scene_frame(self):
        with ui.column():
            with ui.splitter(value=60) as self.splitter:
                self.scene_frame = SceneFrame(self.solution, stl_color="#41684A")
                with self.splitter.after:
                    with ui.column():
                        self.setup_buttons()
                        self.setup_controls()
                with self.splitter.before as self.scene_parent:
                    self.setup_scene()

    def setup_scene(self):
        """
        Setup the scene
        """
        scene = ui.scene(
            width=1700, height=700, grid=True, background_color="#87CEEB"  # Sky blue
        ).classes("w-full h-[700px]")
        self.scene = scene
        self.scene_frame.scene = scene

        self.add_garden3d()
        self.add_lawn()
        self.add_sprinkler()
        self.add_debug_markers()

        self.move_camera()

    def init_control_values(self):
        self.water_particles = []
        self.h_angle_min = 0
        self.h_angle_max = 180
        self.v_angle_min = 0
        self.v_angle_max = 90
        self.h_angle = 90  # Default value within min-max range
        self.v_angle = 45  # Default value within min-max range
        self.water_pressure = 0.5
        self.simulation_speed = 1
        self.is_dynamic = False

    def add_simple_slider(
        self, min: float, max: float, value: float, bind_prop: str, width: str
    ):
        """
        Adds a single slider to the UI.
        """
        return (
            ui.slider(min=min, max=max, value=value)
            .props("label-always")
            .bind_value(self, bind_prop)
            .classes(width)
        )

    def add_slider(
        self,
        min: float,
        max: float,
        value: float or tuple,
        label: str,
        bind_prop: str,
        width: str = "w-32",
        minmax: bool = False,
    ):
        """
        Adds a slider or a pair of min-max sliders to the UI.

        Args:
            min (float): Minimum value of the slider(s).
            max (float): Maximum value of the slider(s).
            value (float or tuple): Initial value of the slider (for single slider) or a tuple (min_value, max_value) for min-max sliders.
            label (str): The label for the slider(s).
            bind_prop (str): The property to bind the slider(s) value(s) to.
            width (str, optional): The CSS class for the slider's width. Defaults to "w-32".
            minmax (bool, optional): Whether to create a pair of min-max sliders. Defaults to False.
        """
        with ui.row() as _slider_row:
            ui.label(f"{label}:")
            if minmax:
                min_value, max_value = value
                min_slider = self.add_simple_slider(
                    min, max, min_value, f"{bind_prop}_min", width
                )
                max_slider = self.add_simple_slider(
                    min, max, max_value, f"{bind_prop}_max", width
                )
                return min_slider, max_slider
            else:
                return self.add_simple_slider(min, max, value, bind_prop, width)

    def setup_controls(self):
        with self.scene_frame.button_row:
            with ui.card() as self.controls_card:
                # Min-max sliders for horizontal and vertical angles
                self.add_slider(
                    min=0,
                    max=180,
                    value=(self.h_angle_min, self.h_angle_max),
                    label="Horizontal Angle °",
                    bind_prop="h_angle",
                    minmax=True,
                )
                self.add_slider(
                    min=0,
                    max=90,
                    value=(self.v_angle_min, self.v_angle_max),
                    label="Vertical Angle °",
                    bind_prop="v_angle",
                    minmax=True,
                )

                # Single sliders for water pressure and simulation speed
                self.add_slider(
                    min=0.1,
                    max=1.5,
                    value=self.water_pressure,
                    label="Water Pressure (bar)",
                    bind_prop="water_pressure",
                )
                self.add_slider(
                    min=0.1,
                    max=10,
                    value=self.simulation_speed,
                    label="Simulation Speed (x)",
                    bind_prop="simulation_speed",
                )

                # Toggle switch for dynamic simulation
                ui.switch("Dynamic Simulation").bind_value(self, "is_dynamic")

    def setup_buttons(self):
        """
        add more buttons
        """
        self.scene_frame.setup_button_row()
        with ui.row() as self.simulation_button_row:
            ui.button("Start Simulation", on_click=self.simulate_sprinkler)
            ui.button("Reset", on_click=self.reset_simulation)

    def reset_simulation(self):
        try:
            if self.scene:
                self.scene_parent.delete(self.scene)
            with self.scene_parent:
                self.setup_scene()
            self.water_particles.clear()
        except Exception as ex:
            self.solution.handle_exception(ex)

    def simulate_sprinkler(self):
        if self.is_dynamic:
            self.simulate_dynamic()
        else:
            self.simulate_static()

    def simulate_static(self, angle_step: int = 5):
        for h_angle in range(self.h_angle_min, self.h_angle_max + 1, angle_step):
            for v_angle in range(self.v_angle_min, self.v_angle_max + 1, angle_step):
                self.create_water_trajectory(h_angle, v_angle)

    def simulate_dynamic(self):
        self.current_h_angle = self.h_angle_min
        self.current_v_angle = self.v_angle_min
        self.h_direction = 1
        self.v_direction = 1

        def update_sprinkler():
            self.sprinkler_head.reset_rotation()
            self.sprinkler_head.rotate(self.current_h_angle, 0, self.current_v_angle)
            self.create_water_trajectory(self.current_h_angle, self.current_v_angle)
            self.remove_old_particles()

            # Update horizontal angle
            self.current_h_angle += self.h_direction * self.simulation_speed
            if (
                self.current_h_angle >= self.h_angle_max
                or self.current_h_angle <= self.h_angle_min
            ):
                self.h_direction *= -1  # Reverse direction

            # Update vertical angle
            self.current_v_angle += self.v_direction * (self.simulation_speed / 2)
            if (
                self.current_v_angle >= self.v_angle_max
                or self.current_v_angle <= self.v_angle_min
            ):
                self.v_direction *= -1  # Reverse direction

        # Use ui.timer for continuous updates
        self.update_timer = ui.timer(0.05, update_sprinkler)

    def create_water_trajectory(self, h_angle, v_angle):
        sprinkler_pos = self.sprinkler_system.config.sprinkler_position
        gravity = 9.8
        initial_velocity = (
            self.water_pressure * 20
        )  # Increased factor for more visible effect

        for t in np.arange(0, 3, 0.1):
            x = sprinkler_pos.x + initial_velocity * t * math.cos(
                math.radians(v_angle)
            ) * math.cos(math.radians(h_angle))
            y = sprinkler_pos.y + initial_velocity * t * math.cos(
                math.radians(v_angle)
            ) * math.sin(math.radians(h_angle))
            z = (
                sprinkler_pos.z
                + initial_velocity * t * math.sin(math.radians(v_angle))
                - 0.5 * gravity * t**2
            )

            if z > 0:
                particle = (
                    self.scene.sphere(0.02)
                    .material("#1E90FF", opacity=0.5)
                    .move(x, y, z)
                )
                self.water_particles.append(particle)

    def remove_old_particles(self):
        max_particles = 500  # Increased for a longer trail
        if len(self.water_particles) > max_particles:
            particles_to_remove = len(self.water_particles) - max_particles
            for _ in range(particles_to_remove):
                old_particle = self.water_particles.pop(0)
                self.scene.remove(old_particle)

    # Add this method to stop the simulation
    def stop_simulation(self):
        if hasattr(self, "update_timer"):
            self.update_timer.cancel()
