"""
Created on 2024-08-30

@author: wf
"""

import math

from ngwidgets.scene_frame import SceneFrame
from nicegui import ui

from sprinkler.slider import GroupPos, SimpleSlider
from sprinkler.sprinkler_core import SprinklerSystem
from sprinkler.waterjet import Point3D


class PivotGroup:
    """
    A class to represent a group of objects
    in a 3D scene with a pivot point for rotation.

    see https://stackoverflow.com/questions/44287255/whats-the-right-way-to-rotate-an-object-around-a-point-in-three-js

    Attributes:
        scene (Scene): The 3D scene containing the objects.
        ap (Point3D): The anchor point where the group is initially placed.
        rp (Point3D): The relative pivot point around which the group will rotate.
        group (Group): The group of objects in the scene, initially positioned at the anchor point.
    """

    def __init__(self, scene_frame, ap: Point3D, rp: Point3D, debug_radius: float = 15):
        self.ap = ap  # anchor point
        self.rp = rp  # relative pivot point
        self.pp = ap + rp  # absolute pivot point
        self.debug_radius = debug_radius
        self.scene_frame = scene_frame
        self.scene = scene_frame.scene
        self.group = self.scene.group().move(x=ap.x, y=ap.y, z=ap.z)

    def load_stl(self, filename, name, cd: Point3D, scale=1, stl_color="#808080"):
        stl_url = f"/examples/{filename}"
        stl_object = self.scene_frame.load_stl(
            filename, stl_url, scale=scale, stl_color=stl_color
        )
        stl_object.name = name
        stl_object.move(x=cd.x, y=cd.y, z=cd.z)
        self.cd = cd
        if self.debug_radius:
            self.pivot_debug(radius=self.debug_radius)

        return stl_object

    def pivot_debug(
        self, radius: float = 15, ap_color: str = "#00ff00", pp_color: str = "#ff0000"
    ):
        """
        show a debug sphere
        """
        with self.group:
            self.pp_sphere = self.scene.sphere(radius).material(
                pp_color
            )  # red sphere for pivot point
        with self.group:
            self.cd_sphere = (
                self.scene.sphere(radius)
                .move(x=self.cd.x, y=self.cd.y, z=self.cd.z)
                .material("#0000ff")  # blue sphere for center point
            )
        self.ap_sphere = (
            self.scene.sphere(radius)
            .move(x=self.ap.x, y=self.ap.y, z=self.ap.z)
            .material(ap_color)  # green sphere for anchor point
        )

    def rotate(self, r: Point3D):
        # Move to origin
        self.group.move(x=-self.rp.x, y=-self.rp.y, z=-self.rp.z)
        # Rotate
        self.group.rotate(math.radians(r.x), math.radians(r.y), math.radians(r.z))
        # Move back
        self.group.move(x=self.rp.x, y=self.rp.y, z=self.rp.z)


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
        self.pos_debug = True

        self.flange_height = 104  # Height of the flange adapter
        self.hose_offset_x = -92
        self.hose_offset_y = -82

        # anchor and pivot calculation
        # base
        self.b_anchor = Point3D(0, 0, self.nema23_size / 2)
        self.b_pivot = Point3D(0, 0, 0)

        # horizontal
        self.h_anchor = Point3D(0, 0, self.flange_height)
        self.h_pivot = Point3D(0, self.nema23_size / 2, self.flange_height)

        # vertical
        self.v_anchor = Point3D(self.hose_offset_x, self.hose_offset_y, 0)
        self.v_pivot = Point3D(0, -self.nema23_size - 20, 0)

        # center delta
        self.nema23_center_delta = Point3D(
            -self.nema23_size / 2, -self.nema23_size / 2, -self.nema23_size / 2
        )
        self.hose_center_delta = Point3D(0, 0, 0)

    def setup_scene(self):
        self.scene_frame = SceneFrame(self.solution, stl_color="#41684A")
        self.scene_frame.setup_button_row()
        self.setup_controls()
        self.scene = ui.scene(
            width=1700,
            height=700,
            grid=(500, 500),
            background_color="#87CEEB",  # Sky blue
        ).classes("w-full h-[700px]")
        self.scene_frame.scene = self.scene

    def setup_ui(self):
        self.setup_scene()

        self.b_group = PivotGroup(
            self.scene_frame, self.b_anchor, self.b_pivot, debug_radius=20
        )
        with self.b_group.group:
            self.motor_h = self.b_group.load_stl(
                "nema23.stl",
                "Horizontal Motor",
                cd=self.nema23_center_delta,
                stl_color="#4682b4",
            )

            self.h_group = PivotGroup(self.scene_frame, self.h_anchor, self.h_pivot)
            with self.h_group.group:
                self.motor_v = self.h_group.load_stl(
                    "nema23.stl", "Vertical Motor", cd=self.nema23_center_delta
                )
                self.motor_v.rotate(math.pi / 2, 0, 0)

                self.v_group = PivotGroup(
                    self.scene_frame, self.v_anchor, self.v_pivot, debug_radius=10
                )
                with self.v_group.group:
                    self.hose = self.v_group.load_stl(
                        "hose.stl", "Hose Snippet", cd=self.hose_center_delta
                    )
                    self.hose.rotate(0, math.pi / 2, 0)

        if self.pos_debug:
            self.setup_sliders()  # Always set up sliders now
        self.move_camera()

    def setup_sliders(self):
        """
        set up debug sliders
        """
        self.b_pivot_slider = GroupPos(
            "b_pivot", self.b_group.group, min_value=-150, max_value=150
        )
        self.h_pivot_slider = GroupPos(
            "h_pivot", self.h_group.group, min_value=-150, max_value=150
        )
        self.v_pivot_slider = GroupPos(
            "v_pivot", self.v_group.group, min_value=-150, max_value=150
        )

    def setup_controls(self):
        with ui.row():
            self.h_angle_slider = SimpleSlider.add_slider(
                min=-180,
                max=180,
                value=0,
                label="Horizontal Angle",
                target=self,
                bind_prop="h_angle",
                width="w-64",
            )
            self.v_angle_slider = SimpleSlider.add_slider(
                min=-180,
                max=180,
                value=0,
                label="Vertical Angle",
                target=self,
                bind_prop="v_angle",
                width="w-64",
            )

        # Add on_change events to update the position
        self.h_angle_slider.on("change", self.update_position)
        self.v_angle_slider.on("change", self.update_position)

    def update_position(self):
        # Apply vertical rotation
        self.v_group.rotate(Point3D(0, self.v_angle, 0))

        # Apply horizontal rotation
        self.h_group.rotate(Point3D(0, 0, self.h_angle))

    def move_camera(self):
        self.scene.move_camera(
            x=0,
            y=-200,  # Move back a bit
            z=150,  # Slightly above the sprinkler
            look_at_x=0,
            look_at_y=0,
            look_at_z=0,
        )
