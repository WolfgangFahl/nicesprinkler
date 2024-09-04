"""
Created on 2024-08-13

@author: wf
"""

from sprinkler.sprinkler_core import SprinklerSystem
from sprinkler.waterjet import Point3D
from tests.sprinkler_base_test import SprinklerBasetest


class TestSprinklerCore(SprinklerBasetest):
    """
    test the SprinklerSystem
    """

    def setUp(self, debug=True, profile=True):
        SprinklerBasetest.setUp(self, debug=debug, profile=profile)
        self.system = SprinklerSystem(self.config_path, self.stl_path)
        self.config = self.system.config

    def test_spray_points_calculation(self):
        """Test spray points calculation"""
        spray_points = self.system.calculate_spray_points()
        self.assertIsInstance(spray_points, list)
        self.assertGreater(len(spray_points), 0)

        max_distance = self.config.hose.max_distance
        for h_angle, v_angle, end_point in spray_points:
            self.assertIsInstance(h_angle, float)
            self.assertIsInstance(v_angle, float)
            self.assertIsInstance(end_point, Point3D)

            # Calculate distance from sprinkler head to end point
            start = self.system.get_spray_origin()
            distance = (
                (end_point.x - start[0]) ** 2
                + (end_point.y - start[1]) ** 2
                + (end_point.z - start[2]) ** 2
            ) ** 0.5

            self.assertLessEqual(distance, max_distance)

    def test_is_point_within_boundaries(self):
        """Test the is_point_within_boundaries method"""
        # Test points within the lawn
        self.assertTrue(self.system.is_point_within_boundaries(Point3D(0.1, 0.1, 0.01)))
        self.assertTrue(
            self.system.is_point_within_boundaries(
                Point3D(
                    self.config.lawn.width - 0.1, self.config.lawn.length - 0.1, 0.01
                )
            )
        )

        # Test points outside the lawn
        self.assertFalse(
            self.system.is_point_within_boundaries(Point3D(-0.1, -0.1, 0.01))
        )
        self.assertFalse(
            self.system.is_point_within_boundaries(
                Point3D(
                    self.config.lawn.width + 0.1, self.config.lawn.length + 0.1, 0.01
                )
            )
        )

        # Test points above max height
        self.assertFalse(
            self.system.is_point_within_boundaries(Point3D(0.1, 0.1, 20))
        )  # Assuming max height is less than 20m

    def test_calculate_trajectory(self):
        """Test the calculate_trajectory method"""
        trajectory = self.system.calculate_trajectory(0, 45)  # Example angles
        self.assertIsInstance(trajectory, list)
        self.assertGreater(len(trajectory), 0)
        for point in trajectory:
            self.assertIsInstance(point, Point3D)
