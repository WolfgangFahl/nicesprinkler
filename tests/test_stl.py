"""
Created on 2024-09-04

@author: wf
"""

from sprinkler.stl import STL
from tests.sprinkler_base_test import SprinklerBasetest


class TestStl(SprinklerBasetest):
    """
    test stl handling
    """

    def setUp(self, debug=True, profile=True):
        SprinklerBasetest.setUp(self, debug=debug, profile=profile)
        self.stl = STL(self.stl_path)

    def test_stl_dimensions(self):
        """Test STL file dimensions against the config"""
        lawn_width, lawn_length = self.config.lawn.width, self.config.lawn.length
