from dataclasses import dataclass

from nicegui import ui

from sprinkler.sprinkler_core import SprinklerSystem
from sprinkler.stepper import Move


@dataclass
class MotorView:
    name: str
    id: int
    position: float = 0
    enabled: bool = False
    slider: ui.slider = None

    def enable(self, move_controller: Move):
        self.enabled = True
        move_controller.enable_motor(self.id)

    def disable(self, move_controller: Move):
        self.enabled = False
        move_controller.disable_motor(self.id)

    def move(self, move_controller: Move, angle: float, rpm: float):
        if self.enabled:
            move_controller.move_motor(self.id, angle, rpm, keep_enabled=self.enabled)
            self.position += angle
            if self.slider:
                self.slider.set_value(self.position)

    def update_position(self, move_controller: Move, new_position: float, rpm: float):
        if self.enabled:
            delta = new_position - self.position
            self.move(move_controller, delta, rpm)


class StepperView:
    def __init__(self, solution, sprinkler_system: SprinklerSystem, step_size: int = 2):
        self.solution = solution
        self.sprinkler_system = sprinkler_system
        self.move_controller = Move()
        self.step_size = step_size
        self.motor_h = MotorView("Horizontal", 1)
        self.motor_v = MotorView("Vertical", 2)

    def setup_ui(self):
        with ui.card():
            ui.label("Stepper Motor Control").classes("text-h6")

            with ui.row():
                ui.button(
                    "Left",
                    icon="left",
                    on_click=lambda: self.motor_h.move(
                        self.move_controller, -self.step_size, self.step_size
                    ),
                )
                ui.button(
                    "Right",
                    icon="right",
                    on_click=lambda: self.motor_h.move(
                        self.move_controller, self.step_size, self.step_size
                    ),
                )
                ui.button(
                    "Up",
                    icon="up",
                    on_click=lambda: self.motor_v.move(
                        self.move_controller, -self.step_size, self.step_size
                    ),
                )
                ui.button(
                    "Down",
                    icon="down",
                    on_click=lambda: self.motor_v.move(
                        self.move_controller, self.step_size, self.step_size
                    ),
                )
                ui.button("Reset", icon="reset", on_click=self.reset_origin)

            with ui.row():
                ui.switch(
                    "H Motor",
                    value=self.motor_h.enabled,
                    on_change=lambda e: self.toggle_motor(self.motor_h, e.value),
                )
                ui.switch(
                    "V Motor",
                    value=self.motor_v.enabled,
                    on_change=lambda e: self.toggle_motor(self.motor_v, e.value),
                )

            ui.label("Horizontal Position")
            self.motor_h.slider = (
                ui.slider(min=0, max=360, value=self.motor_h.position)
                .props("label-always")
                .on(
                    "change",
                    lambda e: self.motor_h.update_position(
                        self.move_controller, e.value, 10
                    ),
                )
            )

            ui.label("Vertical Position")
            self.motor_v.slider = (
                ui.slider(min=0, max=360, value=self.motor_v.position)
                .props("label-always")
                .on(
                    "change",
                    lambda e: self.motor_v.update_position(
                        self.move_controller, e.value, 10
                    ),
                )
            )

    def toggle_motor(self, motor: MotorView, enabled: bool):
        if enabled:
            motor.enable(self.move_controller)
        else:
            motor.disable(self.move_controller)

    def reset_origin(self):
        for motor in [self.motor_h, self.motor_v]:
            if motor.enabled:
                motor.move(self.move_controller, -motor.position, 10)
            motor.position = 0
            motor.slider.set_value(0)

    def cleanup(self):
        self.move_controller.cleanup()
