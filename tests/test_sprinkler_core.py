"""
Created on 2024-08-13

@author: wf
"""

import os

from sprinkler.sprinkler_core import SprinklerConfig, SprinklerSystem
from tests.sprinkler_base_test import SprinklerBasetest


class TestSprinklerCore(SprinklerBasetest):
    """
    Tests for the Sprinkler Core functionality
    """

    def setUp(self, debug=False, profile=True):
        SprinklerBasetest.setUp(self, debug=debug, profile=profile)
        self.system = SprinklerSystem(self.config_path, self.stl_path)
        self.config = self.system.config
        self.stl_analysis = self.system.stl_analysis

    def test_stl_dimensions(self):
        """Test STL file dimensions against the config"""
        stl_width, stl_length, stl_height = self.stl_analysis["dimensions"]
        lawn_width, lawn_length = self.config.lawn.width, self.config.lawn.length
        max_over_width = 2.6
        max_over_length = 2.5
        self.assertLess(stl_width - max_over_width, lawn_width)
        self.assertLess(stl_length - max_over_length, lawn_length)
        self.assertLess(stl_height, 15)  # max expected bush/tree height

    def test_spray_points_calculation(self):
        """Test spray points calculation"""
        spray_points = self.system.calculate_spray_points()
        self.assertIsInstance(spray_points, list)
        self.assertGreater(len(spray_points), 0)

        max_distance = self.config.hose_performance.max_distance
        for _, _, distance in spray_points:
            self.assertLessEqual(distance, max_distance)
