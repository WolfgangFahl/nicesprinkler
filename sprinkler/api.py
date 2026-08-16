"""
Created on 2026-08-16

@author: wf
"""

import os
import uuid
from typing import Optional

from fastapi import Header, HTTPException
from nicegui import app

from sprinkler.camera import CameraView
from sprinkler.stepper import Move


class ApiToken:
    """
    The token that protects the commanding routes.

    It lives in a file of its own beside the installation configuration so
    that it never reaches the settings page, a capture or the repository.
    """

    file_name = "token.yaml"

    def __init__(self, directory: str):
        """
        Args:
            directory: the installation directory of the solution
        """
        self.path = os.path.join(directory, self.file_name)
        self.value = self.read_or_create()

    def read_or_create(self) -> str:
        """
        Read the token, creating it on first start.

        Returns:
            the token value
        """
        value = None
        if os.path.exists(self.path):
            with open(self.path) as token_file:
                for line in token_file:
                    if line.startswith("token:"):
                        value = line.split(":", 1)[1].strip()
        if not value:
            value = str(uuid.uuid4())
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w") as token_file:
                token_file.write(f"token: {value}\n")
            os.chmod(self.path, 0o600)
        return value

    def check(self, given: Optional[str]) -> None:
        """
        Refuse a call that does not carry the token.

        Args:
            given: the value of the token header

        Raises:
            HTTPException: 401 when the token is missing or wrong
        """
        if given != self.value:
            raise HTTPException(status_code=401, detail="invalid token")


class SprinklerApi:
    """
    The commanding routes of the machine.

    The page callbacks and these routes share one Move instance, so the
    remote page and a call cannot disagree about the state of a motor.
    """

    axes = {"h": 1, "v": 2}
    routes_added = False

    def __init__(self, webserver, directory: str):
        """
        Args:
            webserver: the webserver holding the shared Move instance
            directory: the installation directory of the solution
        """
        self.webserver = webserver
        self.token = ApiToken(directory)

    def move_controller(self) -> Move:
        """
        Get the Move instance shared with the remote page.

        Returns:
            the one controller of this process
        """
        controller = getattr(self.webserver, "move_controller", None)
        if controller is None:
            controller = Move(self.webserver.sprinkler_system.config)
            self.webserver.move_controller = controller
        return controller

    def motor_of(self, axis: str):
        """
        Get the motor of the given axis.

        Args:
            axis: h or v

        Returns:
            the motor id

        Raises:
            HTTPException: 404 for an unknown axis
        """
        motor_id = self.axes.get(axis)
        if motor_id is None:
            raise HTTPException(status_code=404, detail="unknown axis")
        return motor_id

    def add_routes(self) -> None:
        """
        Register the commanding routes once per server.
        """
        if SprinklerApi.routes_added:
            return
        api = self

        @app.post("/camera/start")
        def camera_start(x_sprinkler_token: str = Header(None)):
            """Start the camera reader explicitly."""
            api.token.check(x_sprinkler_token)
            CameraView.camera.start()
            return {"available": CameraView.camera.available}

        @app.post("/camera/stop")
        def camera_stop(x_sprinkler_token: str = Header(None)):
            """Stop the camera reader."""
            api.token.check(x_sprinkler_token)
            CameraView.camera.stop()
            return {"available": CameraView.camera.available}

        @app.post("/motor/{axis}/enable")
        def motor_enable(
            axis: str, on: bool = True, x_sprinkler_token: str = Header(None)
        ):
            """Enable or release one axis."""
            api.token.check(x_sprinkler_token)
            motor_id = api.motor_of(axis)
            controller = api.move_controller()
            if on:
                controller.enable_motor(motor_id)
            else:
                controller.disable_motor(motor_id)
            return {"axis": axis, "enabled": controller.motors[motor_id].enabled}

        @app.post("/motor/{axis}/move")
        def motor_move(
            axis: str,
            degrees: float,
            rpm: float = 10,
            x_sprinkler_token: str = Header(None),
        ):
            """Move one axis by the given number of degrees."""
            api.token.check(x_sprinkler_token)
            motor_id = api.motor_of(axis)
            controller = api.move_controller()
            controller.move_motor(motor_id, degrees, rpm, keep_enabled=True)
            return {"axis": axis, "degrees": degrees}

        @app.get("/motor/state")
        def motor_state(x_sprinkler_token: str = Header(None)):
            """Report the enable state of both axes."""
            api.token.check(x_sprinkler_token)
            controller = api.move_controller()
            state = {
                axis: controller.motors[motor_id].enabled
                for axis, motor_id in api.axes.items()
                if motor_id in controller.motors
            }
            return state

        SprinklerApi.routes_added = True
