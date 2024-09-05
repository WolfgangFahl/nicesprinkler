"""
Created on 2024-09-05

@author: wf
"""
from sprinkler.stl3d import STL3D
from mpl_toolkits.mplot3d import Axes3D
from sprinkler.sprinkler_config import Point3D, Lawn
from typing import List

class Garden3D(STL3D):
    def __init__(self, stl_file_path: str, lawn: Lawn):
        super().__init__(stl_file_path)
        self.lawn = lawn
        # Garden-specific parameters (in meters)
        self.hedge_height = 1.8
        self.hedge_width = 1.1
        self.horse_chestnut_x = 2.1
        self.horse_chestnut_y = 7.35
        self.horse_chestnut_trunk_height = 6
        self.horse_chestnut_crown_diameter = 5.5

    def is_point_within_boundaries(self, point: Point3D) -> bool:
        """Check if the point is within the lawn boundaries"""
        return (0 <= point.x <= self.lawn.width and
                0 <= point.y <= self.lawn.length and
                point.z >= 0)

    def is_point_colliding_with_left_hedge(self, point: Point3D) -> bool:
        """Check if the point collides with the left hedge"""
        return (0 <= point.x <= self.hedge_width and
                0 <= point.y <= self.lawn.length - 1.2 and
                0 <= point.z <= self.hedge_height)

    def is_point_colliding_with_second_hedge(self, point: Point3D) -> bool:
        """Check if the point collides with the second hedge"""
        return (self.hedge_width <= point.x <= 2 * self.hedge_width and
                9 <= point.y <= 9 + 1.2 and
                0 <= point.z <= self.hedge_height)

    def is_point_colliding_with_horse_chestnut(self, point: Point3D) -> bool:
        """Check if the point collides with the horse chestnut tree"""
        # Check collision with trunk
        if (abs(point.x - self.horse_chestnut_x) <= 0.45 / 2 and
            abs(point.y - self.horse_chestnut_y) <= 0.45 / 2 and
            0 <= point.z <= self.horse_chestnut_trunk_height):
            return True

        # Check collision with crown
        dx = point.x - self.horse_chestnut_x
        dy = point.y - self.horse_chestnut_y
        dz = point.z - self.horse_chestnut_trunk_height
        distance = (dx**2 + dy**2 + dz**2)**0.5
        return distance <= self.horse_chestnut_crown_diameter / 2

    def is_point_colliding_with_mesh(self, point: Point3D) -> bool:
        """Check if the point collides with any garden element"""
        if self.is_point_colliding_with_left_hedge(point):
            return True
        if self.is_point_colliding_with_second_hedge(point):
            return True
        if self.is_point_colliding_with_horse_chestnut(point):
            return True
        return super().is_point_colliding_with_mesh(point)

    def is_trajectory_valid(self, trajectory: List[Point3D]) -> bool:
        """
        Check if the entire trajectory is valid:
        a) within the boundaries of the garden
        b) not hitting any objects of the 3D STL model or garden elements
        """
        for point in trajectory:
            if not self.is_point_within_boundaries(point):
                return False
            if self.is_point_colliding_with_mesh(point):
                return False
        return True

    def find_collision_point(self, trajectory: List[Point3D]) -> Point3D:
        """
        Find the first point in the trajectory that collides with the mesh or goes out of bounds.
        Returns None if no collision is found.
        """
        for point in trajectory:
            if not self.is_point_within_boundaries(point) or self.is_point_colliding_with_mesh(point):
                return point
        return None

    def visualize(self, ax: Axes3D):
        """Visualize the garden layout in 3D"""
        super().visualize(ax)  # Visualize the STL mesh

        # Plot lawn
        lawn_x = [0, self.lawn.width, self.lawn.width, 0, 0]
        lawn_y = [0, 0, self.lawn.length, self.lawn.length, 0]
        lawn_z = [0, 0, 0, 0, 0]
        ax.plot(lawn_x, lawn_y, lawn_z, 'g-')

        # Plot left hedge
        hedge_x = [0, self.hedge_width, self.hedge_width, 0, 0]
        hedge_y = [0, 0, self.lawn.length - 1.2, self.lawn.length - 1.2, 0]
        hedge_z = [self.hedge_height] * 5
        ax.plot(hedge_x, hedge_y, hedge_z, 'g-')

        # Plot second hedge
        second_hedge_x = [self.hedge_width, 2 * self.hedge_width, 2 * self.hedge_width, self.hedge_width, self.hedge_width]
        second_hedge_y = [9, 9, 10.2, 10.2, 9]
        second_hedge_z = [self.hedge_height] * 5
        ax.plot(second_hedge_x, second_hedge_y, second_hedge_z, 'g-')

        # Plot horse chestnut tree
        ax.plot([self.horse_chestnut_x], [self.horse_chestnut_y], [self.horse_chestnut_trunk_height], 'bo', markersize=10)