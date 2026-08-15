"""
Created on 2026-08-15

@author: wf
"""

import os
import threading
import time
from typing import Iterator, Optional

from nicegui import app, ui
from starlette.responses import PlainTextResponse, Response, StreamingResponse


class Camera:
    """
    A v4l2 camera read directly with linuxpy.

    The camera already delivers MJPEG, so its jpeg frames are passed on
    untouched - no decoding, no encoding, no subprocess. A single reader
    thread keeps the newest frame, which every viewer shares.
    """

    def __init__(
        self,
        device: str = "/dev/video0",
        width: int = 1600,
        height: int = 896,
        fps: int = 5,
    ):
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.latest: Optional[bytes] = None
        self.latest_time: float = 0.0
        self.thread = None
        self.running = False

    @property
    def available(self) -> bool:
        """True if the camera device exists."""
        return os.path.exists(self.device)

    def start(self):
        """Start the reader thread if it is not running yet."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.read_frames, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the reader thread."""
        self.running = False

    def read_frames(self):
        """Keep the newest jpeg frame of the device."""
        from linuxpy.video.device import Device

        with Device(self.device) as cam:
            capture = cam.video_capture
            capture.set_format(self.width, self.height, "MJPG")
            try:
                capture.set_fps(self.fps)
            except Exception:
                # not every driver allows the rate to be set
                pass
            for frame in cam:
                if not self.running:
                    break
                self.latest = bytes(frame)
                self.latest_time = time.time()

    def frame(self) -> bytes:
        """The newest frame as jpeg bytes, empty while none has arrived."""
        return self.latest if self.latest else b""

    def age(self) -> float:
        """Seconds since the newest frame arrived."""
        return time.time() - self.latest_time if self.latest_time else -1.0

    def mjpeg(self) -> Iterator[bytes]:
        """
        Multipart mjpeg stream of the newest frames.

        The browser keeps one connection open and replaces the image in
        place, so there is no reload flicker as with a polled src.
        """
        boundary = b"--frame\r\n"
        last = 0.0
        while True:
            if self.latest and self.latest_time != last:
                last = self.latest_time
                yield boundary + b"Content-Type: image/jpeg\r\n\r\n" + self.latest + b"\r\n"
            time.sleep(1.0 / (self.fps * 2))


class CameraView:
    """
    Live camera view for the remote control page.
    """

    camera = Camera()
    route_added = False

    def __init__(self, solution):
        self.solution = solution
        self.add_route()

    @classmethod
    def add_route(cls):
        """Serve the frames once per server, not once per client."""
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

        @app.get("/camera/age")
        def camera_age():
            return {"age": cls.camera.age(), "fps": cls.camera.fps}

        cls.route_added = True

    def setup_ui(self):
        """Show the live view, or say why there is none."""
        with ui.card().classes("w-full"):
            ui.label("Device Camera").classes("text-h6")
            if not self.camera.available:
                ui.label(f"no camera on {self.camera.device}")
                return
            self.camera.start()
            ui.html(
                '<img src="/camera/stream" style="width:100%;height:auto" '
                'alt="device camera">'
            ).classes("w-full")
