'''
Created on 29.08.2024

@author: wf
'''
import time
from nicegui import ui
from sprinkler.sprinkler_core import SprinklerSystem
from sprinkler.stepper import Move  # Import the Move class from your stepper.py file

class StepperView:
    """
    stepper view
    """
    def __init__(self, solution, sprinkler_system: SprinklerSystem):
        self.solution = solution
        self.sprinkler_system = sprinkler_system
        self.move_controller = Move()
        self.horizontal_position = 0
        self.vertical_position = 0

    def setup_ui(self):
        with ui.card():
            ui.label("Stepper Motor Control").classes("text-h6")

            with ui.row():
                ui.button("Left", on_click=lambda: self.move_calibration(1, -10))
                ui.button("Right", on_click=lambda: self.move_calibration(1, 10))
                ui.button("Down", on_click=lambda: self.move_calibration(2, -10))
                ui.button("Up", on_click=lambda: self.move_calibration(2, 10))

            with ui.row():
                ui.switch("Motor 1 Enabled", on_change=lambda e: self.toggle_motor(1, e.value))
                ui.switch("Motor 2 Enabled", on_change=lambda e: self.toggle_motor(2, e.value))

            ui.label("Horizontal Position")
            self.horizontal_slider = ui.slider(min=0, max=360, value=self.horizontal_position).props('label-always').on('change', lambda e: self.update_position(1, e.value))

            ui.label("Vertical Position")
            self.vertical_slider = ui.slider(min=0, max=360, value=self.vertical_position).props('label-always').on('change', lambda e: self.update_position(2, e.value))

    def move_calibration(self, motor_id: int, angle: float):
        self.move_controller.move_motor(motor_id, angle, 10)  # Using 10 RPM for calibration moves
        if motor_id == 1:
            self.horizontal_position += angle
            self.horizontal_slider.set_value(self.horizontal_position)
        else:
            self.vertical_position += angle
            self.vertical_slider.set_value(self.vertical_position)

    def toggle_motor(self, motor_id: int, enabled: bool):
        if enabled:
            self.move_controller.enable_motor(motor_id)
        else:
            self.move_controller.disable_motor(motor_id)

    def update_position(self, motor_id: int, new_position: float):
        if motor_id == 1:
            delta = new_position - self.horizontal_position
            self.horizontal_position = new_position
        else:
            delta = new_position - self.vertical_position
            self.vertical_position = new_position

        self.move_controller.move_motor(motor_id, delta, 10)  # Using 10 RPM for slider moves

    def cleanup(self):
        self.move_controller.cleanup()

