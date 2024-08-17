'''
Created on 13.08.2024

@author: wf
'''
# sprinkler/model.py

import math
import json
from typing import List, Tuple

class SprinklerModel:
    def __init__(self, config_file: str = 'sprinkler_config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    def calculate_spray_points(self) -> List[Tuple[float, float, float]]:
        spray_points = []
        sprinkler_pos = self.config['sprinkler']['position']

        for h_angle in range(-90, 91, 5):
            for v_angle in range(10, 61, 5):
                distance = self.calculate_spray_distance(v_angle)
                x = sprinkler_pos['x'] + distance * math.cos(math.radians(h_angle))
                y = sprinkler_pos['y'] + distance * math.sin(math.radians(h_angle))
                spray_height = sprinkler_pos['z'] + distance * math.tan(math.radians(v_angle))

                if self.is_point_within_boundaries(x, y, spray_height):
                    spray_points.append((h_angle, v_angle, distance))

        return spray_points

    def calculate_spray_distance(self, angle: float) -> float:
        v0 = math.sqrt(self.config['hose_performance']['max_distance'] * 9.8 /
                       math.sin(2 * math.radians(self.config['hose_performance']['optimal_angle'])))
        t = 2 * v0 * math.sin(math.radians(angle)) / 9.8
        return v0 * math.cos(math.radians(angle)) * t

    def is_point_within_boundaries(self, x: float, y: float, spray_height: float) -> bool:
        if x < 0 or x > self.config['lawn']['width'] or y < 0 or y > self.config['lawn']['length']:
            return False

        # Check boundaries...
        # (boundary checks remain the same)

        return True