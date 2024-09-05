"""
Created on 2024-09-04

@author: wf
"""

import numpy as np
from stl import mesh
from typing import List
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
from sprinkler.sprinkler_config import Point3D

class STL3D:
    """
    Standard Tessellation Language (STL) 3D model file support with visualization.
    """

    def __init__(self, stl_file_path: str):
        self.stl_mesh = mesh.Mesh.from_file(stl_file_path)

    def point_above_triangle(self, point: np.ndarray, triangle: np.ndarray) -> bool:
        """Check if a point is above a triangle in 3D space"""
        v1 = triangle[1] - triangle[0]
        v2 = triangle[2] - triangle[0]
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)
        v = point - triangle[0]
        return np.dot(normal, v) > 0

    def is_point_colliding_with_mesh(self, point: Point3D) -> bool:
        """Check if the point collides with any STL mesh element"""
        point_3d = np.array([point.x * 1000, point.y * 1000, point.z * 1000])  # Convert m to mm
        for triangle in self.stl_mesh.vectors:
            if self.point_above_triangle(point_3d, triangle):
                return True
        return False

    def visualize(self, ax: Axes3D):
        """Visualize the STL model"""
        ax.add_collection3d(mplot3d.art3d.Poly3DCollection(self.stl_mesh.vectors))
        scale = self.stl_mesh.points.flatten()
        ax.auto_scale_xyz(scale, scale, scale)

    def visualize_trajectory(self, trajectory: List[Point3D], ax: Axes3D):
        """Visualize a trajectory in 3D"""
        x, y, z = zip(*[(p.x, p.y, p.z) for p in trajectory])
        ax.plot(x, y, z, 'b-')

    def create_3d_plot(self):
        """Create a 3D plot of the STL model"""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        self.visualize(ax)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('STL Model')
        return fig, ax

    def plot_trajectory(self, trajectory: List[Point3D], title: str):
        """Plot a 2D representation of a trajectory"""
        fig, ax = plt.subplots(figsize=(10, 5))
        x, y, z = zip(*[(p.x, p.y, p.z) for p in trajectory])
        ax.plot(y, z)  # Plot Y vs Z for a side view
        ax.set_xlabel('Y (m)')
        ax.set_ylabel('Z (m)')
        ax.set_title(title)
        ax.grid(True)
        return fig, ax