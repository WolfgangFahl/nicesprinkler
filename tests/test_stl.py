"""
Created on 2024-09-04

@author: wf
"""

import os
import matplotlib.pyplot as plt
from tests.garden_example_stl3d import Garden3D
from sprinkler.sprinkler_config import Point3D, Lawn, Hose
from tests.sprinkler_base_test import SprinklerBasetest
from sprinkler.waterjet import WaterJet

class TestStl(SprinklerBasetest):
    """
    Test STL handling, water jet trajectory validation, and visualization for the specific garden layout
    """

    def setUp(self, debug=True, profile=True):
        SprinklerBasetest.setUp(self, debug=debug, profile=profile)
        self.lawn = Lawn(width=6.1, length=14.6)  # Garden dimensions from the SCAD model
        self.garden = Garden3D(self.stl_path, self.lawn)
        self.output_dir = "/tmp/stl_test_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def test_garden_visualization(self):
        """Test the 3D visualization of the garden layout"""
        fig, ax = self.garden.create_3d_plot()
        plt.savefig(os.path.join(self.output_dir, "garden_layout_3d.png"))
        plt.close(fig)

    def test_trajectory_visualization(self):
        """Test the visualization of water jet trajectories"""
        hose = Hose()  # Assuming default values or you can set specific values
        start_position = Point3D(3, 0, 1)  # Example start position
        water_jet = WaterJet(start_position=start_position, hose=hose)

        angles_to_test = [(30, 30), (45, 45), (60, 60)]  # (horizontal, vertical)

        fig, ax = self.garden.create_3d_plot()

        for h_angle, v_angle in angles_to_test:
            water_jet.set_angles(horizontal_angle=h_angle, vertical_angle=v_angle)
            trajectory = water_jet.calculate_trajectory()

            # Visualize trajectory in 3D
            self.garden.visualize_trajectory(trajectory, ax)

            # Create 2D plot
            fig_2d, ax_2d = self.garden.plot_trajectory(trajectory, f"Trajectory (H: {h_angle}°, V: {v_angle}°)")
            plt.savefig(os.path.join(self.output_dir, f"trajectory_2d_h{h_angle}_v{v_angle}.png"))
            plt.close(fig_2d)

        plt.savefig(os.path.join(self.output_dir, "garden_with_trajectories_3d.png"))
        plt.close(fig)

    def test_collision_detection_with_visualization(self):
        """Test collision detection with visualization"""
        hose = Hose()
        start_position = Point3D(3, 0, 1)
        water_jet = WaterJet(start_position=start_position, hose=hose)

        fig, ax = self.garden.create_3d_plot()

        # Test a trajectory that should collide with the left hedge
        water_jet.set_angles(horizontal_angle=180, vertical_angle=30)
        trajectory = water_jet.calculate_trajectory()
        self.garden.visualize_trajectory(trajectory, ax)

        collision_point = self.garden.find_collision_point(trajectory)
        if collision_point:
            ax.plot([collision_point.x], [collision_point.y], [collision_point.z], 'ro', markersize=10, label='Collision Point')

        plt.savefig(os.path.join(self.output_dir, "collision_detection_3d.png"))
        plt.close(fig)

        # Create 2D plot of the colliding trajectory
        fig_2d, ax_2d = self.garden.plot_trajectory(trajectory, "Colliding Trajectory")
        if collision_point:
            ax_2d.plot(collision_point.y, collision_point.z, 'ro', markersize=10, label='Collision Point')
        ax_2d.legend()
        plt.savefig(os.path.join(self.output_dir, "collision_detection_2d.png"))
        plt.close(fig_2d)

        self.assertIsNotNone(collision_point, "Expected a collision with the left hedge")
