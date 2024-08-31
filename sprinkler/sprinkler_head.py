import math
from nicegui import ui
from ngwidgets.scene_frame import SceneFrame

class SprinklerHeadView:
    """
    Sprinkler head with vertical and horizontal Nema 23 motors
    and garden hose attached via cable tie to the flange coupling
    """
    def __init__(self, solution):
        self.solution = solution
        self.scene = None
        self.motor_h = None
        self.motor_v = None
        self.hose = None
        self.h_angle = 0
        self.v_angle = 0
        self.h_motor_group = None
        self.v_motor_group = None

        self.setup_ui()
        self.reset_camera()

    def setup_scene(self):
        self.scene_frame = SceneFrame(self.solution, stl_color="#41684A")
        self.scene_frame.setup_button_row()
        # Setup controls
        self.setup_controls()
        self.scene = ui.scene(
            width=1700, height=700, grid=True, background_color="#87CEEB"  # Sky blue
        ).classes("w-full h-[700px]")
        self.scene_frame.scene = self.scene

    def load_stl(self, filename, name, scale=1):
        stl_url = f"/examples/{filename}"
        return self.scene_frame.load_stl(filename, stl_url, scale=scale)

    def setup_ui(self):
        # Dimensions (in meters)
        motor_height = 0.0528  # 2.08 inches
        motor_width = 0.0572   # 2.25 inches (NEMA 23 width)
        flange_height = 0.013  # 13mm
        hose_length = 0.060    # 60mm

        # prepares scene
        self.setup_scene()

        with self.scene.group() as self.h_motor_group:
            # Load STL models
            self.motor_h = self.load_stl("nema23.stl", "Horizontal Motor")

            with self.scene.group() as self.v_motor_group:
                self.motor_v = self.load_stl("nema23.stl", "Vertical Motor")
                # Position vertical motor on top of horizontal motor
                self.motor_v.rotate(math.pi/2, 0, 0)  # Rotate 90 degrees around X-axis
                self.motor_v.move(y=motor_height/2 + motor_width/2, z=motor_width/2)
                self.hose = self.load_stl("hose.stl", "Hose Snippet")

                # Position hose attached to the side of the vertical motor's flange coupling
                self.hose.rotate(0, math.pi/2, 0)  # Rotate 90 degrees around Y-axis
                self.hose.move(x=motor_width/2 + hose_length/2, y=motor_height/2 + motor_width/2, z=motor_width/2)

    def setup_controls(self):
        with ui.card():
            ui.label("Sprinkler Head Control").classes("text-h6")

            with ui.row():
                ui.number("Horizontal Angle", value=0, format="%.2f").bind_value(self, "h_angle").on("change", self.update_position)
                ui.number("Vertical Angle", value=0, format="%.2f").bind_value(self, "v_angle").on("change", self.update_position)

    def update_position(self):
        # Update horizontal motor group rotation
        self.h_motor_group.clear_transforms()
        self.h_motor_group.rotate(0, 0, math.radians(self.h_angle))

        # Update vertical motor group rotation
        self.v_motor_group.clear_transforms()
        self.v_motor_group.rotate(0, math.radians(self.v_angle), 0)

    def reset_camera(self):
        # Set a better default camera position
        self.scene.camera.position = (0.2, 0.2, 0.2)
        self.scene.camera.look_at((0, 0, 0))