"""
Created on 2024-08-13

@author: wf
"""

from sprinkler.sprinkler_core import SprinklerSystem, SprinklerConfig
from tests.sprinkler_base_test import SprinklerBasetest


class TestSprinklerCore(SprinklerBasetest):
    """
    test the SprinklerSystem
    """

    def setUp(self, debug=True, profile=True):
        SprinklerBasetest.setUp(self, debug=debug, profile=profile)
        self.system = SprinklerSystem(self.config_path, self.stl_path)
        self.config = self.system.config

    def test_sprinkler_system_initialization(self):
        self.assertIsInstance(self.system.config, SprinklerConfig)
        self.assertEqual(self.system.stl_file_path, self.stl_path)