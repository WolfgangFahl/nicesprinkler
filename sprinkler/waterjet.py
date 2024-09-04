"""
Created on 2024-08-27

Author: wf
"""

import math
from typing import List

from sprinkler.sprinkler_config import Hose, Point3D


class Parabolic:
    """
    Parabolic trajectory calculations.
    """

    def __init__(
        self,
        start_position: Point3D,
        initial_velocity: float,
        horizontal_angle: float,
        vertical_angle: float,
        gravity: float = 9.8,
    ):
        self.start_position = start_position
        self.initial_velocity = initial_velocity
        self.horizontal_angle = horizontal_angle
        self.vertical_angle = vertical_angle
        self.gravity = gravity

    def calculate_trajectory(self, num_segments: int = 20) -> List[Point3D]:
        """
        Calculate the parabolic trajectory as a series of points (line segments).

        Args:
            num_segments (int): Number of segments to divide the trajectory into.

        Returns:
            List[Point3D]: A list of points representing the trajectory.
        """
        v_rad = math.radians(self.vertical_angle)
        h_rad = math.radians(self.horizontal_angle)
        v0_x = self.initial_velocity * math.cos(v_rad) * math.cos(h_rad)
        v0_y = self.initial_velocity * math.cos(v_rad) * math.sin(h_rad)
        v0_z = self.initial_velocity * math.sin(v_rad)

        t_max = (
            v0_z + math.sqrt(v0_z**2 + 2 * self.gravity * self.start_position.z)
        ) / self.gravity
        t_step = t_max / num_segments

        points = []
        for i in range(num_segments + 1):
            t = i * t_step
            x = self.start_position.x + v0_x * t
            y = self.start_position.y + v0_y * t
            z = self.start_position.z + v0_z * t - 0.5 * self.gravity * t**2
            points.append(Point3D(x, y, max(0, z)))  # Ensure z is not negative

        return points

    def get_line_segments(self) -> List[tuple]:
        """
        Get the trajectory as a list of line segments for rendering.

        Returns:
            List[tuple]: A list of tuples, each containing two points representing a line segment.
        """
        points = self.calculate_trajectory()
        return [
            (points[i].to_tuple(), points[i + 1].to_tuple())
            for i in range(len(points) - 1)
        ]


class WaterJet:
    """
    Water jet calculations for a sprinkler.
    Handles the configuration of the water jet and calculates the trajectory using the Parabolic class.
    """

    def __init__(self, start_position: Point3D, hose: Hose):
        """
        Initialize the WaterJet with a starting position and hose configuration.

        Args:
            start_position (Point3D): The starting position of the water jet.
            hose (Hose): The hose configuration providing velocity and other properties.
        """
        self.start_position = start_position
        self.hose = hose
        self.horizontal_angle = None
        self.vertical_angle = None
        self.parabolic = None  # Initialize as None

    def set_angles(self, horizontal_angle: float, vertical_angle: float):
        """
        Set the horizontal and vertical angles and initialize the Parabolic trajectory.

        Args:
            horizontal_angle (float): The horizontal angle of the spray.
            vertical_angle (float): The vertical angle of the spray.
        """
        self.horizontal_angle = horizontal_angle
        self.vertical_angle = vertical_angle
        self.parabolic = Parabolic(
            start_position=self.start_position,
            initial_velocity=self.hose.velocity,
            horizontal_angle=horizontal_angle,
            vertical_angle=vertical_angle,
        )

    def calculate_trajectory(self, num_segments: int = 20) -> List[Point3D]:
        """
        Calculate the parabolic trajectory as a series of points.

        Args:
            num_segments (int): Number of segments to divide the trajectory into.

        Returns:
            List[Point3D]: A list of points representing the trajectory.
        """
        if self.parabolic is None:
            raise ValueError(
                "Parabolic trajectory is not initialized. Call set_angles first."
            )
        return self.parabolic.calculate_trajectory(num_segments)

    def get_line_segments(self) -> List[tuple]:
        """
        Get the trajectory as a list of line segments for rendering.

        Returns:
            List[tuple]: A list of tuples, each containing two points representing a line segment.
        """
        if self.parabolic is None:
            raise ValueError(
                "Parabolic trajectory is not initialized. Call set_angles first."
            )
        return self.parabolic.get_line_segments()
