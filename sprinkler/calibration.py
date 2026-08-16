"""
Created on 2026-08-15

@author: wf
"""

import time

from nicegui import ui

from sprinkler.sprinkler_core import SprinklerSystem


class FlowMeasurement:
    """
    A single bucket fill measurement.
    """

    def __init__(self, bucket_size: float):
        self.bucket_size = bucket_size
        self.start_time = None
        self.seconds = None

    def start(self):
        """Start the stop watch."""
        self.start_time = time.monotonic()
        self.seconds = None

    def stop(self):
        """Stop the stop watch and keep the elapsed time."""
        self.seconds = self.elapsed()
        self.start_time = None

    @property
    def running(self) -> bool:
        return self.start_time is not None

    def elapsed(self) -> float:
        """Seconds since start, or the measured time when stopped."""
        if self.start_time is not None:
            return time.monotonic() - self.start_time
        return self.seconds if self.seconds else 0.0

    @property
    def liter_per_second(self) -> float:
        return self.bucket_size / self.seconds if self.seconds else 0.0

    @property
    def liter_per_minute(self) -> float:
        return self.liter_per_second * 60


class CalibrationView:
    """
    Flow calibration by filling a bucket of known size against a stop watch.
    """

    def __init__(self, solution, sprinkler_system: SprinklerSystem):
        self.solution = solution
        self.sprinkler_system = sprinkler_system
        self.measurement = FlowMeasurement(bucket_size=10)
        self.timer = None

    def setup_ui(self):
        with ui.card():
            ui.label("Flow Calibration").classes("text-h6")

            ui.label("Bucket size in liters")
            ui.slider(
                min=5,
                max=30,
                step=1,
                value=self.measurement.bucket_size,
                on_change=lambda e: self.set_bucket_size(e.value),
            ).props("label-always")

            with ui.row():
                self.watch_button = ui.button(
                    "Start", icon="timer", on_click=self.toggle_watch
                )
                self.apply_button = ui.button(
                    "Apply to configuration", icon="save", on_click=self.apply
                )
                self.apply_button.disable()

            self.elapsed_label = ui.label("0.0 s").classes("text-h5")
            self.result_label = ui.label("")

            self.timer = ui.timer(0.1, self.update_elapsed)

    def set_bucket_size(self, liters: float):
        self.measurement.bucket_size = liters

    def toggle_watch(self):
        """Start the watch on the first click, stop it on the second."""
        if self.measurement.running:
            self.measurement.stop()
            self.watch_button.set_text("Start")
            self.apply_button.enable()
            self.show_result()
        else:
            self.measurement.start()
            self.watch_button.set_text("Stop")
            self.apply_button.disable()
            self.result_label.set_text("")

    def update_elapsed(self):
        self.elapsed_label.set_text(f"{self.measurement.elapsed():.1f} s")

    def show_result(self):
        m = self.measurement
        self.result_label.set_text(
            f"{m.bucket_size:.0f} l in {m.seconds:.1f} s "
            f"= {m.liter_per_second:.3f} l/s = {m.liter_per_minute:.2f} l/min"
        )

    def apply(self):
        """
        Take the measured flow rate into the hose configuration and save it.
        """
        try:
            hose = self.sprinkler_system.config.hose
            hose.calibrate(
                max_distance=hose.max_distance,
                max_height=hose.max_height,
                flow_rate=self.measurement.liter_per_minute,
            )
            config_path = self.sprinkler_system.config_path
            self.sprinkler_system.config.save_to_yaml_file(config_path)
            ui.notify(
                f"flow rate {self.measurement.liter_per_minute:.2f} l/min saved to {config_path}"
            )
        except Exception as ex:
            ui.notify(f"Error saving calibration: {str(ex)}", color="red")
