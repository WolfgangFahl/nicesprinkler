'''
Created on 13.08.2024

@author: wf
'''

from ngwidgets.yamlable import lod_storable
from dataclasses import field
from typing import Dict

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
class Boundary:
    """
    Boundary information
    """
    type: str
    height: float
    distance: float

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
    boundaries: Dict[str, Boundary] = field(default_factory=dict)
    motors: Dict[str, MotorConfig] = field(default_factory=dict)


class SprinklerSystem:
    """
    Main sprinkler system class
    """
    config: SprinklerConfig

    def calculate_spray_points(self):
        # Implementation
        pass

    def is_point_within_boundaries(self, x: float, y: float, spray_height: float) -> bool:
        # Implementation
        pass

    def calculate_spray_distance(self, angle: float) -> float:
        # Implementation
        pass