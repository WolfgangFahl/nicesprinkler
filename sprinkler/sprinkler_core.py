"""
Created on 2024-08-13

@author: wf
"""

from stl import mesh

from sprinkler.sprinkler_config import SprinklerConfig


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
        return np.array(
            [
                self.config.sprinkler_position.x,
                self.config.sprinkler_position.y,
                self.config.sprinkler_position.z,
            ]
        )

    def calculate_spray_points(self):
        spray_points = []
        h_range = self.config.angles.horizontal
        v_range = self.config.angles.vertical

        for h_angle in np.arange(h_range.min, h_range.max + h_range.step, h_range.step):
            for v_angle in np.arange(
                v_range.min, v_range.max + v_range.step, v_range.step
            ):
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
