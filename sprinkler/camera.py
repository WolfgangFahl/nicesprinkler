"""
Created on 2026-08-15

@author: wf
"""

import os
import subprocess
import tempfile
import time
from typing import Iterator

from nicegui import app, ui
from starlette.responses import PlainTextResponse, Response, StreamingResponse


class Camera:
    """
    A v4l2 camera kept as a running stream so that the automatic exposure
    stays converged.

    A single grabbed frame is unusable - the exposure needs about 60 frames
    to settle, which costs some 10 s per picture. ffmpeg therefore writes
    the newest frame to a file continuously and the page reads that file.
    """

    def __init__(
        self,
        device: str = "/dev/video0",
        width: int = 1600,
        height: int = 896,
        fps: int = 2,
    ):
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.process = None
        self.frame_path = os.path.join(tempfile.gettempdir(), "nicesprinkler_devcam.jpg")

    @property
    def available(self) -> bool:
        """True if the camera device exists."""
        return os.path.exists(self.device)

    def start(self):
        """Start the ffmpeg stream if it is not running yet."""
        if self.process and self.process.poll() is None:
            return
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-loglevel", "error",
            "-f", "v4l2",
            "-input_format", "mjpeg",
            "-video_size", f"{self.width}x{self.height}",
            "-i", self.device,
            "-vf", f"fps={self.fps}",
            "-update", "1",
            "-y", self.frame_path,
        ]
        self.process = subprocess.Popen(cmd)

    def stop(self):
        """Stop the ffmpeg stream."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
        self.process = None

    def frame(self) -> bytes:
        """The newest frame as jpeg bytes, empty while none has been written."""
        if not os.path.exists(self.frame_path):
            return b""
        with open(self.frame_path, "rb") as jpeg:
            return jpeg.read()

    def mjpeg(self) -> Iterator[bytes]:
        """
        Multipart mjpeg stream of the newest frames.

        The browser keeps one connection open and replaces the image in
        place, so there is no reload flicker as with a polled src.
        """
        boundary = b"--frame\r\n"
        while True:
            jpeg = self.frame()
            if jpeg:
                yield boundary + b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
            time.sleep(1.0 / self.fps)


class CameraView:
    """
    Live camera view for the remote control page.
    """

    camera = Camera()
    route_added = False

    def __init__(self, solution):
        self.solution = solution
        self.counter = 0
        self.add_route()

    @classmethod
    def add_route(cls):
        """Serve the newest frame once per server, not once per client."""
        if cls.route_added:
            return

        @app.get("/camera/frame")
        def camera_frame():
            jpeg = cls.camera.frame()
            if not jpeg:
                return PlainTextResponse("no frame", status_code=503)
            return Response(
                content=jpeg,
                media_type="image/jpeg",
                headers={"Cache-Control": "no-store"},
            )

        @app.get("/camera/stream")
        def camera_stream():
            return StreamingResponse(
                cls.camera.mjpeg(),
                media_type="multipart/x-mixed-replace; boundary=frame",
            )

        cls.route_added = True

    def setup_ui(self):
        """Show the live view, or say why there is none."""
        with ui.card().classes("w-full"):
            ui.label("Device Camera").classes("text-h6")
            if not self.camera.available:
                ui.label(f"no camera on {self.camera.device}")
                return
            self.camera.start()
            # the mjpeg stream replaces the picture in place - no polling,
            # no reload flicker
            ui.html(
                '<img src="/camera/stream" style="width:100%;height:auto" '
                'alt="device camera">'
            ).classes("w-full")
