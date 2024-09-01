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

        self.flange_height = 104  # Height of the flange adapter
        self.hose_offset_x = -92
        self.hose_offset_y = -82

        # Pivot and offset calculations
        self.hp_x = 0
        self.hp_y = self.nema23_size / 2
        self.hp_z = self.flange_height

        self.vp_x = self.hose_offset_x
        self.vp_y = self.hose_offset_y
        self.vp_z = 0

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
        self.setup_scene()

        with self.scene.group() as self.base_group:
            self.motor_h = self.load_stl("nema23.stl", "Horizontal Motor", stl_color="#4682b4")

            with self.scene.group().move(x=self.hp_x,y=self.hp_y,z=self.hp_z) as self.h_rotation_group:
                self.scene.sphere(2, '#ff0000')  # Red sphere for horizontal pivot
                self.motor_v = self.load_stl("nema23.stl", "Vertical Motor")
                self.motor_v.rotate(math.pi/2, 0, 0)

                with self.scene.group().move(x=self.vp_x, y=self.vp_y, z=self.vp_z) as self.v_rotation_group:
                    self.scene.sphere(2, '#ff0000')  # Red sphere for vertical pivot
                    self.hose = self.load_stl("hose.stl", "Hose Snippet")
                    self.hose.rotate(0, math.pi/2, 0)

        self.setup_sliders()  # Always set up sliders now
        self.move_camera()

    def setup_sliders(self):
        self.h_pivot_slider = GroupPos("h_pivot", self.h_rotation_group, min_value=-100, max_value=100)
        self.v_pivot_slider = GroupPos("v_pivot", self.v_rotation_group, min_value=-100, max_value=100)

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