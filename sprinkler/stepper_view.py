from dataclasses import dataclass

from nicegui import ui

from sprinkler.sprinkler_core import SprinklerSystem
from sprinkler.stepper import Move, StepperMotor


@dataclass
class MotorView:
    """
    One motor on the remote control page.

    The enable state is not remembered here - it is read from the pin, so
    a page reload or a reconnect cannot make the page and the machine
    disagree.
    """

    name: str
    id: int
    motor: StepperMotor = None
    position: float = 0
    slider: ui.slider = None

    @property
    def enabled(self) -> bool:
        return self.motor.enabled if self.motor else False

    def enable(self, move_controller: Move):
        move_controller.enable_motor(self.id)

    def disable(self, move_controller: Move):
        move_controller.disable_motor(self.id)

    def move(self, move_controller: Move, angle: float, rpm: float):
        if self.enabled:
            move_controller.move_motor(self.id, angle, rpm, keep_enabled=True)
            self.position += angle
            if self.slider:
                self.slider.set_value(self.position)

    def update_position(self, move_controller: Move, new_position: float, rpm: float):
        if self.enabled:
            delta = new_position - self.position
            self.move(move_controller, delta, rpm)


class StepperView:
    """
    Remote control page for the two stepper motors.
    """

    def __init__(self, solution, sprinkler_system: SprinklerSystem, step_size: int = 2):
        self.solution = solution
        self.sprinkler_system = sprinkler_system
        # one controller per process - see the enable state note in Move
        self.move_controller = getattr(solution.webserver, "move_controller", None)
        if self.move_controller is None:
            self.move_controller = Move(sprinkler_system.config)
            solution.webserver.move_controller = self.move_controller
        self.step_size = step_size
        self.motor_h = MotorView("Horizontal", 1, self.move_controller.motors.get(1))
        self.motor_v = MotorView("Vertical", 2, self.move_controller.motors.get(2))

    def setup_ui(self):
        with ui.card():
            ui.label("Stepper Motor Control").classes("text-h6")

            with ui.row():
                ui.button(
                    "Left",
                    icon="arrow_back",
                    on_click=lambda: self.motor_h.move(
                        self.move_controller, -self.step_size, self.step_size
                    ),
                )
                ui.button(
                    "Right",
                    icon="arrow_forward",
                    on_click=lambda: self.motor_h.move(
                        self.move_controller, self.step_size, self.step_size
                    ),
                )
                ui.button(
                    "Up",
                    icon="arrow_upward",
                    on_click=lambda: self.motor_v.move(
                        self.move_controller, -self.step_size, self.step_size
                    ),
                )
                ui.button(
                    "Down",
                    icon="arrow_downward",
                    on_click=lambda: self.motor_v.move(
                        self.move_controller, self.step_size, self.step_size
                    ),
                )
                ui.button("Reset", icon="restart_alt", on_click=self.reset_origin)

            with ui.row():
                # the value comes from the pin, not from memory
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
            self.motor_h.slider = ui.slider(
                min=0,
                max=360,
                value=self.motor_h.position,
                on_change=lambda e: self.motor_h.update_position(
                    self.move_controller, e.value, 10
                ),
            ).props("label-always")

            ui.label("Vertical Position")
            self.motor_v.slider = ui.slider(
                min=0,
                max=360,
                value=self.motor_v.position,
                on_change=lambda e: self.motor_v.update_position(
                    self.move_controller, e.value, 10
                ),
            ).props("label-always")

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
