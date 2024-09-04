"""
Created on 2024-08-13

@author: wf
"""

from sprinkler.sprinkler_config import Point3D, SprinklerConfig


class SprinklerSystem:
    """
    Main sprinkler system class
    """

    def __init__(self, config_path: str, stl_file_path: str):
        self.stl_file_path = stl_file_path
        self.config = SprinklerConfig.load_from_yaml_file(config_path)

    def is_point_within_boundaries(self, point: Point3D) -> bool:
        # Check if the point is within the lawn boundaries
        if not (
            0 <= point.x <= self.config.lawn.width
            and 0 <= point.y <= self.config.lawn.length
            and point.z >= 0
        ):
            return False

        # Check if the point is above any STL mesh element
        point_3d = np.array(
            [point.x * 1000, point.y * 1000, point.z * 1000]
        )  # Convert m to mm
        for triangle in self.stl_mesh.vectors:
            if self.point_above_triangle(point_3d, triangle):
                return False

        return True

    def point_above_triangle(self, point, triangle):
        v1 = triangle[1] - triangle[0]
        v2 = triangle[2] - triangle[0]
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)
        v = point - triangle[0]
        return np.dot(normal, v) > 0
