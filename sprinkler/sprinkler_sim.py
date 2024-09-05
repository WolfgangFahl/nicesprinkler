"""
Created on 2024-08-13

@author: wf
"""

import os
from typing import List

from ngwidgets.scene_frame import SceneFrame
from nicegui import ui

from sprinkler.slider import SimpleSlider
from sprinkler.sprinkler_core import SprinklerSystem
from sprinkler.waterjet import Point3D, WaterJet  # Import the existing WaterJet module


class SprinklerSimulation:
    """
    Simulate lawn sprinkling
    """

    def __init__(self, solution, sprinkler_system: SprinklerSystem):
        self.solution = solution
        self.sprinkler_system = sprinkler_system

        self.lawn_width = self.sprinkler_system.config.lawn.width
        self.lawn_length = self.sprinkler_system.config.lawn.length
        self.lawn_height = 0.05

        self.cx = self.lawn_width / 2
        self.cy = self.lawn_length / 2

        self.scene = None
        self.sprinkler_head = None
        self.sprinkler_model = None
        self.init_control_values()

        self.water_lines = []
        self.total_water_sprinkled = 0  # in liters
        self.sprinkling_time = 0  # in seconds

        self.time_label = None
        self.flow_label = None
        self.coverage_label = None

    def init_control_values(self):
        """
        initialize the control values
        """
        self.h_angle_min = self.sprinkler_system.config.angles.horizontal.min
        self.h_angle_max = self.sprinkler_system.config.angles.horizontal.max
        self.v_angle_min = self.sprinkler_system.config.angles.vertical.min
        self.v_angle_max = self.sprinkler_system.config.angles.vertical.max
        self.h_angle = self.sprinkler_system.config.angles.horizontal.initial
        self.v_angle = self.sprinkler_system.config.angles.vertical.initial
        self.water_pressure = self.sprinkler_system.config.hose.pressure
        self.simulation_speed = 1
        self.is_dynamic = False
        self.flow_rate = self.sprinkler_system.config.hose.flow_rate

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
        scene = ui.scene(
            width=1700, height=700, grid=True, background_color="#87CEEB"
        ).classes("w-full h-[700px]")
        self.scene = scene
        self.scene_frame.scene = scene

        self.add_garden3d()
        self.add_lawn()
        self.add_sprinkler()
        self.move_camera()

    def setup_controls(self):
        with self.scene_frame.button_row:
            with ui.expansion("Controls", icon="work").classes("w-full"):
                with ui.card() as self.controls_card:
                    SimpleSlider.add_slider(
                        min=self.h_angle_min,
                        max=self.h_angle_max,
                        value=(self.h_angle_min, self.h_angle_max),
                        label="Horizontal Angle °",
                        target=self,
                        bind_prop="h_angle",
                        minmax=True,
                    )
                    SimpleSlider.add_slider(
                        min=self.v_angle_min,
                        max=self.v_angle_max,
                        value=(self.v_angle_min, self.v_angle_max),
                        label="Vertical Angle °",
                        target=self,
                        bind_prop="v_angle",
                        minmax=True,
                    )
                    SimpleSlider.add_slider(
                        min=0.1,
                        max=10,
                        value=self.simulation_speed,
                        label="Simulation Speed (x)",
                        target=self,
                        bind_prop="simulation_speed",
                    )
                    ui.switch("Dynamic Simulation").bind_value(self, "is_dynamic")
                    self.flow_number = ui.number().bind_value(self, "flow_rate")

    def setup_buttons(self):
        self.scene_frame.setup_button_row()
        with ui.row() as self.simulation_button_row:
            self.simulation_button = self.solution.tool_button(
                "toggle simulation",
                handler=self.toggle_simulation,
                icon="play_circle",
                toggle_icon="stop_circle",
            )
            self.flow_measurement_button = self.solution.tool_button(
                "toggle flow measurement",
                handler=self.toggle_flow_measurement,
                icon="clock_start",
                toggle_icon="clock_stop",
            )
            ui.button("Reset", on_click=self.reset_simulation, icon="restart_alt")
        with ui.row() as self.progress_row:
            self.time_label = ui.label("Time: 00:00")
            self.flow_label = ui.label("Total Flow: 0.00 L")
            self.coverage_label = ui.label("Coverage:  0.0%")

    def toggle_simulation(self):
        self.solution.toggle_icon(self.simulation_button)
        if self.has_icon_name(self.simulation_button, "stop_circle"):
            self.start_simulation()
        else:
            self.stop_simulation()

    def start_simulation(self):
        if self.is_dynamic:
            self.simulate_dynamic()
        else:
            self.simulate_static()

    def stop_simulation(self):
        if hasattr(self, "update_timer"):
            self.update_timer.cancel()

    def has_icon_name(self, button, icon_name):
        result = button._props["icon"] == icon_name
        return result

    def toggle_flow_measurement(self):
        """
        toggle the flow measurement
        """
        self.solution.toggle_icon(self.flow_measurement_button)
        if self.has_icon_name(self.flow_measurement_button.icon, "clock_stop"):
            self.flow_measurement_start_time = self.sprinkling_time
            self.flow_measurement_volume = 0
        else:
            elapsed_time = self.sprinkling_time - self.flow_measurement_start_time
            flow_rate = (
                self.flow_measurement_volume / elapsed_time
            ) * 60  # Convert to l/min
            ui.notify(f"Flow rate: {flow_rate:.2f} l/min")

    def update_water_info(self):
        """
        update time an flow labels
        """
        lawn = self.sprinkler_system.config.lawn
        total_water_needed = (
            lawn.rain_mm_to_l()
        )  # Uses the default rainfall_mm if not specified

        coverage = min(100, (self.total_water_sprinkled / total_water_needed) * 100)
        minutes, seconds = divmod(int(self.sprinkling_time), 60)
        self.time_label.set_text(f"Time: {minutes:02d}:{seconds:02d}")
        self.flow_label.set_text(f"Total Flow: {self.total_water_sprinkled:.2f} L")
        self.coverage_label.set_text(f"Coverage: {coverage:.2f}%")

    def reset_simulation(self):
        try:
            self.stop_simulation()
            self.solution.toggle_icon(self.simulation_button)
            self.solution.toggle_icon(self.flow_measurement_button)
            self.total_water_sprinkled = 0
            self.sprinkling_time = 0
            self.update_water_info()

            # Remove all water lines
            for line in self.water_lines:
                line.delete()
            self.water_lines.clear()
        except Exception as ex:
            self.solution.handle_exception(ex)

    def simulate_static(self):
        def update_static():
            try:
                sprinkler_pos = self.sprinkler_system.config.sprinkler_head
                jet = WaterJet(
                    start_position=Point3D(
                        sprinkler_pos.x, sprinkler_pos.y, sprinkler_pos.z
                    ),
                    hose=self.sprinkler_system.config.hose,
                )
                jet.set_angles(self.h_angle, self.v_angle)
                trajectory = jet.calculate_trajectory()
                self.draw_water_line(trajectory)
                self.update_water_info()

                if self.has_icon_name(self.simulation_button, "play_circle"):
                    self.update_timer.cancel()
            except Exception as ex:
                self.solution.handle_exception(ex)

        self.update_timer = ui.timer(0.5, update_static)

    def simulate_dynamic(self):
        self.current_h_angle = self.h_angle_min
        self.current_v_angle = self.v_angle_min
        self.h_direction = 1
        self.v_direction = 1

        def update_dynamic():
            try:
                sprinkler_pos = self.sprinkler_system.config.sprinkler_head
                jet = WaterJet(
                    start_position=Point3D(
                        sprinkler_pos.x, sprinkler_pos.y, sprinkler_pos.z
                    ),
                    hose=self.sprinkler_system.config.hose,
                )
                jet.set_angles(self.current_h_angle, self.current_v_angle)
                trajectory = jet.calculate_trajectory()
                self.draw_water_line(trajectory)
                self.update_water_info()

                # Update angles
                self.current_h_angle += self.h_direction * self.simulation_speed
                if (
                    self.current_h_angle >= self.h_angle_max
                    or self.current_h_angle <= self.h_angle_min
                ):
                    self.h_direction *= -1

                self.current_v_angle += self.v_direction * (self.simulation_speed / 2)
                if (
                    self.current_v_angle >= self.v_angle_max
                    or self.current_v_angle <= self.v_angle_min
                ):
                    self.v_direction *= -1

                if self.has_icon_name(self.simulation_button, "play_circle"):
                    self.update_timer.cancel()
            except Exception as ex:
                self.solution.handle_exception(ex)

        self.update_timer = ui.timer(0.05, update_dynamic)

    def draw_water_line(self, trajectory: List[Point3D]):
        for i in range(len(trajectory) - 1):
            start = trajectory[i].to_tuple()
            end = trajectory[i + 1].to_tuple()
            line = self.scene.line(start, end)
            line.material("#1E90FF", opacity=0.7)
            self.water_lines.append(line)

        # Calculate water sprinkled
        time_step = 0.05  # seconds
        self.total_water_sprinkled += (
            self.flow_rate / 60
        ) * time_step  # Convert l/min to l/s
        self.sprinkling_time += time_step

        # Remove old lines if there are too many
        while len(self.water_lines) > 1000:
            old_line = self.water_lines.pop(0)
            old_line.delete()

    def add_lawn(self):
        with self.scene.group().move(x=self.cx, y=self.cy):
            self.scene.box(
                self.lawn_width, self.lawn_length, self.lawn_height
            ).material("#7CFC00")

    def add_garden3d(self):
        stl_filename = os.path.basename(self.sprinkler_system.stl_file_path)
        stl_url = f"/examples/{stl_filename}"
        self.garden_model = self.scene_frame.load_stl(
            stl_filename, stl_url, scale=0.001
        )

    def add_sprinkler(self):
        sprinkler_pos = self.sprinkler_system.config.sprinkler_head
        sprinkler_height = sprinkler_pos.z
        with self.scene.group().move(x=sprinkler_pos.x, y=sprinkler_pos.y, z=0):
            self.scene.box(width=0.2, height=0.2, depth=sprinkler_height).material(
                "#FF4500"
            ).move(z=sprinkler_height / 2)
            self.sprinkler_head = (
                self.scene.sphere(0.05).material("#4682B4").move(z=sprinkler_height)
            )

    def move_camera(self):
        self.scene.move_camera(
            x=self.cx,
            y=-self.lawn_length * 0.4,
            z=self.lawn_length / 2,
            look_at_x=self.cx,
            look_at_y=self.cy,
            look_at_z=0,
        )
