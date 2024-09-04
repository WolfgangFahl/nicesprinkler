"""
Created on 2024-09-03

@author: wf
"""

import math
from dataclasses import field
from typing import List

from ngwidgets.yamlable import lod_storable
from tabulate import tabulate


@lod_storable
class Point3D:
    x: float
    y: float
    z: float

    def __add__(self, other):
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, scalar):
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def to_tuple(self):
        return (self.x, self.y, self.z)


@lod_storable
class Lawn:
    """
    Lawn dimensions (meter)
    """

    width: float
    length: float
    rainfall_mm: float = (
        10  # default rainfall equivalent needed to properly wet the lawn
    )

    area: float = field(init=False)  # This field is not expected as input

    def __post_init__(self):
        # Calculate the area after the object is initialized
        self.area = self.width * self.length

    def rain_mm_to_l(self, rainfall_mm: float = None) -> float:
        """
        Calculate the volume of rainwater in liters given the rainfall in millimeters.
        """
        # 1 mm of rain on 1 square meter equals 1 liter of water
        if rainfall_mm is None:
            rainfall_mm = self.rainfall_mm
        return self.area * rainfall_mm


class SprinklerHead(Point3D):
    """
    Sprinkler head position relative to lawn (meter)
    """


@lod_storable
class AngleRange:
    """
    Defines a range of angles with a minimum, maximum, and step size and
    precaluclated angles
    """

    min: float
    max: float
    initial: float
    step: float
    angles: List[float] = field(init=False)

    def __post_init__(self):
        # Generate the list of angles based on the provided range
        self.angles = self.generate_angles()

    def generate_angles(self) -> List[float]:
        """
        Generate a list of angles based on the AngleRange specification.
        """
        angles = []
        current = self.min
        while current <= self.max:
            angles.append(current)
            current += self.step
        return angles


@lod_storable
class Angles:
    """
    Angle configuration for the sprinkler
    """

    horizontal: AngleRange
    vertical: AngleRange


@lod_storable
class Hose:
    """
    Hose specifications with calibration capabilities.
    """

    diameter: float = 25.4 / 2  # half inch hose, diameter in mm
    flow_rate: float = 11.5  # flow rate in l/min
    max_distance: float = 7.4  # Maximum horizontal distance reached (meters)
    max_height: float = 3.35  # Maximum vertical height reached (meters)

    pressure: float = field(init=False)  # Pressure in bar, will be calculated
    velocity: float = field(init=False)  # Velocity in m/s, will be calculated
    nozzle_area: float = field(
        init=False
    )  # Nozzle area in square mm, will be calculated
    nozzle_diameter: float = field(
        init=False
    )  # Nozzle diameter in mm, will be calculated

    def __post_init__(self):
        self.recalculate()

    def calibrate(self, max_distance: float, max_height: float, flow_rate: float):
        """
        Calibrate the hose based on measured values.
        """
        self.max_distance = max_distance
        self.max_height = max_height
        self.flow_rate = flow_rate
        self.recalculate()

    def recalculate(self):
        # Use max_height to calculate initial velocity
        self.velocity = math.sqrt(2 * 9.8 * self.max_height)

        # Calculate nozzle area in square mm
        self.nozzle_area = (self.flow_rate / 60) / (self.velocity * 1000) * 1e6
        self.nozzle_diameter = 2 * math.sqrt(
            self.nozzle_area / math.pi
        )  # Diameter in mm

        # Calculate pressure in bar
        self.pressure = self.max_height * 9.8 / 100

    def spray_distance(self, angle: float) -> float:
        """
        Calculate the spray distance for the given angle of spray.
        """
        t = 2 * self.velocity * math.sin(math.radians(angle)) / 9.8
        spray_distance = self.velocity * math.cos(math.radians(angle)) * t
        return spray_distance

    def specs(self, tablefmt: str = "pipe") -> str:
        """
        Return the hose specifications as a formatted string using tabulate.

        Args:
           tablefmt (str): The table format to use (default: 'pipe')
        Returns:
            str: Formatted string of hose specifications
        """
        data = [
            ["Hose Diameter", f"{self.diameter:.2f} mm"],
            ["Flow Rate", f"{self.flow_rate:.2f} L/min"],
            ["Nozzle Diameter", f"{self.nozzle_diameter:.2f} mm"],
            ["Nozzle Area", f"{self.nozzle_area:.2f} mm²"],
            ["Initial Velocity", f"{self.velocity:.2f} m/s"],
            ["Pressure", f"{self.pressure:.2f} bar"],
            ["Maximum Spray Distance (45°)", f"{self.spray_distance(45):.2f} m"],
            ["Maximum Vertical Height", f"{self.max_height:.2f} m"],
            ["Maximum Horizontal Distance", f"{self.max_distance:.2f} m"],
        ]

        markup = tabulate(data, headers=["Specification", "Value"], tablefmt=tablefmt)
        return markup


@lod_storable
class Motor:
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
class Motors:
    """
    Motor configurations
    """

    horizontal: Motor
    vertical: Motor


@lod_storable
class SprinklerConfig:
    """
    Complete configuration for the sprinkler system
    """

    lawn: Lawn
    sprinkler_head: SprinklerHead
    angles: Angles
    hose: Hose
    motors: Motors = field(default_factory=dict)
