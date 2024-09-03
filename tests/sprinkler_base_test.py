"""
Created on 03.09.2024

@author: wf
"""

import os

from ngwidgets.basetest import Basetest

from sprinkler.sprinkler_config import SprinklerConfig


class SprinklerBasetest(Basetest):
    """
    Basetest for Sprinkler modules
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        examples_dir = os.path.join(
            os.path.dirname(__file__), "..", "nicesprinkler_examples"
        )
        self.config_path = os.path.join(examples_dir, "example_config.yaml")
        self.stl_path = os.path.join(examples_dir, "example_garden.stl")
        self.config = SprinklerConfig.load_from_yaml_file(self.config_path)
