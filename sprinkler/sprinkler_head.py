"""
Created on 2024-08-30

@author: wf
"""
import math
from nicegui import ui
from ngwidgets.scene_frame import SceneFrame
from sprinkler.sprinkler_core import SprinklerSystem
from sprinkler.slider import GroupPos, SimpleSlider

class SprinklerHeadView:
    """
    Sprinkler head with vertical and horizontal Nema 23 motors
    and garden hose attached via cable tie to the flange coupling

    all units are in mm
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
        self.nema23_size = 56
        self.pos_debug = False

        # Define pivot points and offsets
        self.flange_height = 104  # Height of the flange adapter
        self.hose_offset_x = -92
        self.hose_offset_y = -82

    def setup_scene(self):
        self.scene_frame = SceneFrame(self.solution, stl_color="#41684A")
        self.scene_frame.setup_button_row()
        self.setup_controls()
        self.scene = ui.scene(
            width=1700, height=700,
            grid=(500, 500),
            background_color="#87CEEB"  # Sky blue
        ).classes("w-full h-[700px]")
        self.scene_frame.scene = self.scene

    def load_stl(self, filename, name, scale=1, stl_color="#808080"):
        stl_url = f"/examples/{filename}"
        return self.scene_frame.load_stl(filename, stl_url, scale=scale, stl_color=stl_color)

    def setup_ui(self):
        """
        setup the user interface
        """
        self.setup_scene()

        sprinkler_pos = self.sprinkler_system.config.sprinkler_position

        with self.scene.group().move(x=sprinkler_pos.x, y=sprinkler_pos.y, z=sprinkler_pos.z) as self.sprinkler_group:
            # Base group for horizontal rotation
            with self.scene.group() as self.base_group:
                self.motor_h = self.load_stl("nema23.stl", "Horizontal Motor", stl_color="#4682b4")

                # Group for vertical rotation
                with self.scene.group().move(y=self.nema23_size/2, z=self.flange_height) as self.h_rotation_group:
                    with self.scene.group() as self.v_motor_group:
                        self.motor_v = self.load_stl("nema23.stl", "Vertical Motor")
                        self.motor_v.rotate(math.pi/2, 0, 0)  # 90 degree rotated

                    # Hose group
                    with self.scene.group().move(x=self.hose_offset_x, y=self.hose_offset_y) as self.v_rotation_group:
                        self.hose = self.load_stl("hose.stl", "Hose Snippet")
                        self.hose.rotate(0, math.pi/2, 0)

        if self.pos_debug:
            self.setup_sliders()
        self.move_camera()

    def setup_controls(self):
        with ui.row():
            self.h_angle_slider = SimpleSlider.add_slider(
                min=-180, max=180, value=0, label="Horizontal Angle",
                target=self, bind_prop="h_angle", width="w-64"
            )
            self.v_angle_slider = SimpleSlider.add_slider(
                min=-90, max=90, value=0, label="Vertical Angle",
                target=self, bind_prop="v_angle", width="w-64"
            )

        # Add on_change events to update the position
        self.h_angle_slider.on("change", self.update_position)
        self.v_angle_slider.on("change", self.update_position)

    def setup_sliders(self):
        if self.pos_debug:
            v_pos = GroupPos("v", self.v_motor_group, min_value=0, max_value=150)
            hose_pos = GroupPos("hose", self.hose_group, min_value=-100, max_value=100)

    def update_position(self):
        # Apply horizontal rotation
        self.h_rotation_group.rotate(0, 0, math.radians(self.h_angle))

        # Apply vertical rotation
        self.v_rotation_group.rotate(0, math.radians(self.v_angle), 0)

    def move_camera(self):
        self.scene.move_camera(
            x=0,
            y=-200,  # Move back a bit
            z=150,  # Slightly above the sprinkler
            look_at_x=0,
            look_at_y=0,
            look_at_z=0,
        )