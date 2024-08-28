"""
Created on 2024-08-13

@author: wf
"""

from dataclasses import field
from typing import Dict

import numpy as np
from ngwidgets.yamlable import lod_storable
from stl import mesh


@lod_storable
class Lawn:
    """
    Lawn dimensions in meters
    """

    width: float
    length: float


@lod_storable
class SprinklerPosition:
    """
    Sprinkler position in the lawn
    """

    x: float
    y: float
    z: float


@lod_storable
class Angles:
    """
    Initial angles for the sprinkler
    """

    horizontal: float
    vertical: float


@lod_storable
class HosePerformance:
    """
    Hose performance specifications
    """

    max_distance: float
    optimal_angle: float


@lod_storable
class MotorConfig:
    """
    Configuration for a single motor
    """

    ena_pin: int
    dir_pin: int
    pul_pin: int
    steps_per_revolution: int
    min_angle: int
    max_angle: int


@lod_storable
class SprinklerConfig:
    """
    Complete configuration for the sprinkler system
    """

    lawn: Lawn
    sprinkler_position: SprinklerPosition
    initial_angles: Angles
    hose_performance: HosePerformance
    motors: Dict[str, MotorConfig] = field(default_factory=dict)


class SprinklerSystem:
    """
    Main sprinkler system class
    """

    def __init__(self, config_path: str, stl_file_path: str):
        self.stl_file_path = stl_file_path
        self.config = SprinklerConfig.load_from_yaml_file(config_path)
        self.stl_mesh = mesh.Mesh.from_file(stl_file_path)
        self.stl_analysis = self.analyze_stl()

    def analyze_stl(self):
        """Analyze the STL file to determine key points for spray calculation"""
        stl_min = np.min(self.stl_mesh.vectors, axis=(0, 1))
        stl_max = np.max(self.stl_mesh.vectors, axis=(0, 1))
        stl_dimensions = stl_max - stl_min
        spray_origin = self.get_spray_origin()
        return {
            "min": stl_min,
            "max": stl_max,
            "dimensions": stl_dimensions,
            "spray_origin": spray_origin,
        }

    def get_spray_origin(self):
        """Get the spray origin from the config"""
        return np.array(
            [
                self.config.sprinkler_position.x,
                self.config.sprinkler_position.y,
                self.config.sprinkler_position.z,
            ]
        )

    def calculate_spray_points(self):
        spray_points = []
        for h_angle in range(
            -90, 91, 5
        ):  # horizontal angles from -90 to 90 in 5-degree steps
            for v_angle in range(
                10, 61, 5
            ):  # vertical angles from 10 to 60 in 5-degree steps
                distance = self.calculate_spray_distance(v_angle)
                x = self.stl_analysis["spray_origin"][0] + distance * np.cos(
                    np.radians(h_angle)
                )
                y = self.stl_analysis["spray_origin"][1] + distance * np.sin(
                    np.radians(h_angle)
                )
                spray_height = self.stl_analysis["spray_origin"][2] + distance * np.tan(
                    np.radians(v_angle)
                )

                if self.is_point_within_boundaries(x, y, spray_height):
                    spray_points.append((h_angle, v_angle, distance))

        return spray_points

    def is_point_within_boundaries(
        self, x: float, y: float, spray_height: float
    ) -> bool:
        return 0 <= x <= self.config.lawn.width and 0 <= y <= self.config.lawn.length

    def calculate_spray_distance(self, angle: float) -> float:
        v0 = np.sqrt(
            self.config.hose_performance.max_distance
            * 9.8
            / np.sin(2 * np.radians(self.config.hose_performance.optimal_angle))
        )
        t = 2 * v0 * np.sin(np.radians(angle)) / 9.8
        return v0 * np.cos(np.radians(angle)) * t
