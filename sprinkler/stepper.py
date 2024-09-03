"""
Created on 13.08.2024

@author: wf
"""

"""
stepper.py

Control two stepper motors connected to a Raspberry Pi through a TB6600 driver to sprinkle a lawn.

Author: Wolfgang, ChatGPT, Claude AI
Date: 2024-07 to 2024-08
"""

import argparse
import time
from typing import Dict

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    # Create a dummy GPIO module if the import fails (for non-Raspberry Pi environments)
    print(
        "RPi.GPIO module not found. Using a mock version for non-Raspberry Pi environment."
    )

    class GPIO:
        BOARD = None
        OUT = None
        HIGH = None
        LOW = None

        @staticmethod
        def setmode(mode):
            pass

        @staticmethod
        def setup(pin, mode):
            pass

        @staticmethod
        def output(pin, state):
            pass

        @staticmethod
        def cleanup():
            pass


class StepperMotor:
    def __init__(
        self,
        name: str,
        ena_pin: int,
        dir_pin: int,
        pul_pin: int,
        steps_per_revolution: int = 200,
    ):
        self.name = name
        self.ena_pin = ena_pin
        self.dir_pin = dir_pin
        self.pul_pin = pul_pin
        self.steps_per_revolution = steps_per_revolution
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setup(self.ena_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.pul_pin, GPIO.OUT)
        GPIO.output(self.ena_pin, GPIO.HIGH)  # Start with motor disabled

    def enable(self):
        GPIO.output(self.ena_pin, GPIO.LOW)

    def disable(self):
        GPIO.output(self.ena_pin, GPIO.HIGH)

    def set_direction(self, clockwise: bool):
        GPIO.output(self.dir_pin, GPIO.HIGH if clockwise else GPIO.LOW)

    def step(self, steps: int, delay: float):
        for _ in range(abs(steps)):
            GPIO.output(self.pul_pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.pul_pin, GPIO.LOW)
            time.sleep(delay)


class Move:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.motors: Dict[int, StepperMotor] = {
            1: StepperMotor("Motor1", 37, 35, 33),
            2: StepperMotor("Motor2", 31, 29, 23),
        }

    def enable_motor(self, motor_id: int):
        motor = self.motors.get(motor_id)
        if motor:
            motor.enable()
        else:
            print(f"Motor {motor_id} not found")

    def disable_motor(self, motor_id: int):
        motor = self.motors.get(motor_id)
        if motor:
            motor.disable()
        else:
            print(f"Motor {motor_id} not found")

    def move_motor(
        self, motor_id: int, angle: float, speed_rpm: float, keep_enabled: bool = False
    ):
        motor = self.motors.get(motor_id)
        if not motor:
            print(f"Motor {motor_id} not found")
            return
        steps = int(abs(angle) / 360 * motor.steps_per_revolution)
        delay = 30 / (speed_rpm * motor.steps_per_revolution)
        motor.enable()
        motor.set_direction(angle >= 0)
        motor.step(steps, delay)
        if not keep_enabled:
            motor.disable()

    def perform_pattern(
        self,
        horizontal_angle: float,
        horizontal_steps: int,
        vertical_angle: float,
        rpm: float,
    ):
        # Enable both motors before starting the pattern
        self.enable_motor(1)
        self.enable_motor(2)

        for _ in range(horizontal_steps):
            self.move_motor(1, horizontal_angle, rpm, keep_enabled=True)
            self.move_motor(2, vertical_angle, rpm, keep_enabled=True)
            self.move_motor(2, -vertical_angle, rpm, keep_enabled=True)

        # Reset horizontal position
        self.move_motor(1, -horizontal_angle * horizontal_steps, rpm, keep_enabled=True)

        # Disable both motors after completing the pattern
        self.disable_motor(1)
        self.disable_motor(2)

    def perform_pattern_by_args(self, pattern_args):
        # Default values
        params = {"steps": 80, "hangle": 160, "vangle": 120, "rpm": 10}

        # Parse provided arguments
        for arg in pattern_args:
            key, value = arg.split("=")
            if key in params:
                params[key] = float(value)

        # Execute the pattern
        self.perform_pattern(
            horizontal_angle=params["hangle"] / params["steps"],
            horizontal_steps=int(params["steps"]),
            vertical_angle=params["vangle"],
            rpm=params["rpm"],
        )

    def cleanup(self):
        for motor in self.motors.values():
            motor.disable()
        GPIO.cleanup()
        time.sleep(0.1)


# Modify main function to use the new approach
def main():
    parser = argparse.ArgumentParser(description="Control stepper motors")
    parser.add_argument(
        "-m", "--motor", type=int, default=1, help="Motor ID (default: 1)"
    )
    parser.add_argument(
        "-a",
        "--angle",
        type=float,
        default=15,
        help="Angle to rotate (default: 15, positive for CW, negative for CCW)",
    )
    parser.add_argument(
        "-r", "--rpm", type=float, default=20, help="Speed in RPM (default: 20)"
    )
    parser.add_argument(
        "-k",
        "--keep-enabled",
        action="store_true",
        help="Keep motor enabled after movement",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        nargs="*",
        metavar="KEY=VALUE",
        help="Perform pattern: [steps=N] [hangle=DEG] [vangle=DEG] [rpm=RPM] default: steps=20,hangle=160,vangle=90,rpm=10",
    )

    args = parser.parse_args()
    move_controller = Move()

    if args.pattern is not None:
        # For pattern, we'll handle enabling/disabling within the perform_pattern method
        move_controller.perform_pattern_by_args(args.pattern)
    else:
        # For single motor movement
        move_controller.move_motor(args.motor, args.angle, args.rpm, args.keep_enabled)

    move_controller.cleanup()


if __name__ == "__main__":
    main()
