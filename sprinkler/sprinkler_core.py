"""
Created on 2024-08-13

@author: wf
"""

from sprinkler.sprinkler_config import SprinklerConfig
from sprinkler.stl3d import STL3D

class SprinklerSystem:
    """
    Main sprinkler system class
    """

    def __init__(self, config_path: str, stl_file_path: str):
        self.stl_file_path = stl_file_path
        self.config = SprinklerConfig.load_from_yaml_file(config_path)
        self.stl=STL3D(stl_file_path)


