"""
Created on 2024-09-04

@author: wf
"""

import numpy as np
from stl import mesh


class STL:
    """
    Standard Tessellation Language (STL) 3D model file support
    """

    def __init__(self, stl_file_path: str):
        # load  the Standard Tessellation Language (STL) 3D model file
        self.stl_mesh = mesh.Mesh.from_file(stl_file_path)
