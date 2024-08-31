"""
Created on 2024-08-30

@author: wf
"""
import math
from nicegui import ui
from ngwidgets.scene_frame import SceneFrame
from sprinkler.sprinkler_core import SprinklerSystem

class SprinklerHeadView:
    """
    Sprinkler head with vertical and horizontal Nema 23 motors
    and garden hose attached via cable tie to the flange coupling
    """
    def __init__(self, solution, sprinkler_system: SprinklerSystem):
        self.solution = solution
        self.sprinkler_system = sprinkler_system
        self.scene = None
        self.motor_h = None
        self.motor_v = None
        self.hose = None
        self.h_angle = 0
        self.v_angle = 0
        self.h_motor_group = None
        self.v_motor_group = None


    def setup_scene(self):
        self.scene_frame = SceneFrame(self.solution, stl_color="#41684A")
        self.scene_frame.setup_button_row()
        self.setup_controls()
        self.scene = ui.scene(
            width=1700, height=700, grid=True, background_color="#87CEEB"  # Sky blue
        ).classes("w-full h-[700px]")
        self.scene_frame.scene = self.scene

    def load_stl(self, filename, name, scale=0.001):
        stl_url = f"/examples/{filename}"
        return self.scene_frame.load_stl(filename, stl_url, scale=scale)

    def setup_ui(self):
        self.setup_scene()

        sprinkler_pos = self.sprinkler_system.config.sprinkler_position

        with self.scene.group().move(x=sprinkler_pos.x, y=sprinkler_pos.y, z=sprinkler_pos.z) as self.sprinkler_group:
            with self.scene.group() as self.h_motor_group:
                self.motor_h = self.load_stl("nema23.stl", "Horizontal Motor")

                with self.scene.group() as self.v_motor_group:
                    self.motor_v = self.load_stl("nema23.stl", "Vertical Motor")
                    self.motor_v.rotate(math.pi/2, 0, 0)
                    self.motor_v.move(y=0.0528/2 + 0.0572/2, z=0.0572/2)  # Using NEMA 23 dimensions

                    self.hose = self.load_stl("hose.stl", "Hose Snippet")
                    self.hose.rotate(0, math.pi/2, 0)
                    self.hose.move(x=0.0572/2 + 0.060/2, y=0.0528/2 + 0.0572/2, z=0.0572/2)
        self.move_camera()

    def setup_controls(self):
        with ui.card():
            ui.label("Sprinkler Head Control").classes("text-h6")

            with ui.row():
                ui.number("Horizontal Angle", value=0, format="%.2f").bind_value(self, "h_angle").on("change", self.update_position)
                ui.number("Vertical Angle", value=0, format="%.2f").bind_value(self, "v_angle").on("change", self.update_position)

    def update_position(self):
        self.h_motor_group.clear_transforms()
        self.h_motor_group.rotate(0, 0, math.radians(self.h_angle))

        self.v_motor_group.clear_transforms()
        self.v_motor_group.rotate(0, math.radians(self.v_angle), 0)

    def move_camera(self):
        sprinkler_pos = self.sprinkler_system.config.sprinkler_position

        self.scene.move_camera(
            x=sprinkler_pos.x,
            y=sprinkler_pos.y - 0.2,  # Move back a bit
            z=sprinkler_pos.z + 0.15,  # Slightly above the sprinkler
            look_at_x=sprinkler_pos.x,
            look_at_y=sprinkler_pos.y,
            look_at_z=sprinkler_pos.z,
        )