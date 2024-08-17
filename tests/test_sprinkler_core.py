'''
Created on 13.08.2024

@author: wf
'''
from ngwidgets.basetest import Basetest
from sprinkler.sprinkler_core import SprinklerConfig, SprinklerSystem
import os

class TestSprinklerCore(Basetest):
    """
    Tests for the Sprinkler Core functionality
    """

    def setUp(self):
        super().setUp()
        self.test_config_path = os.path.join(os.path.dirname(__file__), "..", "nicegui_examples", "example_config.yaml")

    def test_config(self):
        self.assertTrue(os.path.isfile(self.test_config_path))