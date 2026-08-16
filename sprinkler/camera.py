"""
Created on 2026-08-15

@author: wf
"""

import json
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
        from linuxpy.video.device import Device, VideoCapture

        with Device(self.device) as cam:
            capture = VideoCapture(cam)
            capture.set_format(self.width, self.height, "MJPG")
            try:
                capture.set_fps(self.fps)
            except Exception:
                # not every driver lets the rate be set
                pass
            with capture:
                for frame in capture:
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


class Recorder:
    """
    Writes camera frames with the commanded motor angles beside them.

    A frame without its commanded position is not calibration data, so
    every frame gets a json sidecar of the same name.
    """

    def __init__(self, camera: "Camera", stepper=None, base_dir: str = None):
        self.camera = camera
        self.stepper = stepper
        self.base_dir = base_dir or os.path.expanduser("~/nicesprinkler_records")
        self.session_id = None
        self.session_dir = None
        self.frame_no = 0
        self.recording = False

    def start(self, fpm: int) -> str:
        """Open a session directory and start counting frames."""
        self.session_id = time.strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(self.base_dir, self.session_id)
        os.makedirs(self.session_dir, exist_ok=True)
        self.frame_no = 0
        self.fpm = fpm
        self.recording = True
        return self.session_dir

    def stop(self):
        self.recording = False

    def angles(self) -> dict:
        """The commanded angles, or nulls when no stepper view is attached."""
        if self.stepper is None:
            return {
                "commanded_h_angle": None,
                "commanded_v_angle": None,
                "h_enabled": None,
                "v_enabled": None,
            }
        return {
            "commanded_h_angle": self.stepper.motor_h.position,
            "commanded_v_angle": self.stepper.motor_v.position,
            "h_enabled": self.stepper.motor_h.enabled,
            "v_enabled": self.stepper.motor_v.enabled,
        }

    def record_frame(self) -> Optional[str]:
        """Write one frame and its sidecar; returns the frame path."""
        if not self.recording:
            return None
        jpeg = self.camera.frame()
        if not jpeg:
            return None
        stamp = time.strftime("%Y%m%d_%H%M%S")
        name = f"{stamp}_{self.frame_no:05d}"
        frame_path = os.path.join(self.session_dir, f"{name}_devcam.jpg")
        with open(frame_path, "wb") as out:
            out.write(jpeg)
        sidecar = {
            "session_id": self.session_id,
            "frame_no": self.frame_no,
            "file": os.path.basename(frame_path),
            "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "monotonic": time.monotonic(),
            "frame_age": self.camera.age(),
            "frames_per_minute": self.fpm,
            "width": self.camera.width,
            "height": self.camera.height,
        }
        sidecar.update(self.angles())
        with open(os.path.join(self.session_dir, f"{name}.json"), "w") as out:
            json.dump(sidecar, out, indent=2)
        self.frame_no += 1
        return frame_path


class CameraView:
    """
    Live camera view for the remote control page.
    """

    camera = Camera()
    route_added = False

    def __init__(self, solution, stepper=None):
        self.solution = solution
        self.recorder = Recorder(self.camera, stepper)
        self.timer = None
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
            self.setup_recording()

    def setup_recording(self):
        """Record button and frames per minute slider."""
        self.fpm = 60
        with ui.row().classes("items-center w-full"):
            self.record_button = ui.button(
                "Record", icon="fiber_manual_record", on_click=self.toggle_record
            )
            ui.label("frames per minute")
            ui.slider(
                min=1,
                max=120,
                step=1,
                value=self.fpm,
                on_change=lambda e: self.set_fpm(e.value),
            ).props("label-always").classes("w-64")
        self.record_label = ui.label("")

    def set_fpm(self, fpm: int):
        self.fpm = int(fpm)

    def toggle_record(self):
        """Start the recording on the first click, stop it on the second."""
        if self.recorder.recording:
            self.recorder.stop()
            if self.timer:
                self.timer.deactivate()
            self.record_button.set_text("Record")
            self.record_label.set_text(
                f"{self.recorder.frame_no} frames in {self.recorder.session_dir}"
            )
        else:
            session_dir = self.recorder.start(self.fpm)
            self.timer = ui.timer(60.0 / self.fpm, self.record_frame)
            self.record_button.set_text("Stop")
            self.record_label.set_text(f"recording to {session_dir}")

    def record_frame(self):
        self.recorder.record_frame()
        self.record_label.set_text(
            f"{self.recorder.frame_no} frames in {self.recorder.session_dir}"
        )
