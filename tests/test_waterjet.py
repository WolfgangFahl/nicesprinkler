"""
Created on 2024-08-29

Author: wf
"""

import math
import os

import matplotlib.pyplot as plt
import numpy as np
from ngwidgets.basetest import Basetest

from sprinkler.sprinkler_config import Hose
from sprinkler.waterjet import Point3D, WaterJet


class TestWaterjetVisual(Basetest):
    """
    Visual tests for Waterjet functionality
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.output_dir = "/tmp/waterjet_test"
        os.makedirs(self.output_dir, exist_ok=True)
        self.hose = Hose()
        self.hose.calibrate(7.4, 3.35, 12 / (63 / 60))

    def test_water_jet(self):
        """
        Test the water jet calculations
        """
        wj = WaterJet(start_position=Point3D(0, 0, 1), hose=self.hose)
        wj.set_angles(horizontal_angle=45, vertical_angle=30)
        trajectory = wj.calculate_trajectory()

        # Assertions to validate the trajectory
        self.assertIsInstance(trajectory, list)
        self.assertGreater(len(trajectory), 0)

        # Check the first and last points
        self.assertEqual(trajectory[0], wj.start_position)
        self.assertEqual(trajectory[-1].z, 0)  # Should end at ground level

    def test_real_life_data(self):
        """
        Test and generate visualizations using real-life test data
        """
        # Test data provided by the user
        test_data = [
            {"d": 0.26, "pressure": 0.01},
            {"d": 0.36, "pressure": 0.02},
            {"d": 0.40, "pressure": 0.02},
            {"d": 0.84, "pressure": 0.04},
            {"d": 1.20, "pressure": 0.06},
            {"d": 4.20, "pressure": 0.21},
            {"d": 4.20, "pressure": 0.21},
            {"d": 7.00, "pressure": 0.34},
            {"d": 11.00, "pressure": 0.54},
            {"d": 13.00, "pressure": 0.64},
        ]

        for index, data in enumerate(test_data):
            # Calibrate the hose with max_distance and derive max_height from pressure
            self.hose.calibrate(
                max_distance=data["d"],
                max_height=data["pressure"] * 10.2,
                flow_rate=self.hose.flow_rate,
            )

            wj = WaterJet(start_position=Point3D(0, 0, 1), hose=self.hose)
            wj.set_angles(horizontal_angle=45, vertical_angle=45)
            trajectory = wj.calculate_trajectory()

            # Plot and save results
            fig, ax = plt.subplots(figsize=(10, 5))

            # Plot expected parabolic trajectory using hose.velocity
            t_expected = np.linspace(
                0, 2 * self.hose.velocity * math.sin(math.radians(45)) / 9.8, 100
            )
            x_expected = self.hose.velocity * t_expected * math.cos(math.radians(45))
            z_expected = (
                self.hose.velocity * t_expected * math.sin(math.radians(45))
                - 0.5 * 9.8 * t_expected**2
                + wj.start_position.z
            )
            ax.plot(x_expected, z_expected, "r--", label="Expected Parabola")

            # Plot calculated trajectory
            x, y, z = zip(*[(p.x, p.y, p.z) for p in trajectory])
            ax.plot(x, z, label="Calculated Trajectory")

            ax.legend()
            ax.set_xlabel("X (m)")
            ax.set_ylabel("Z (m)")
            ax.set_title(
                f'Test {index + 1}: d={data["d"]}m, pressure={data["pressure"]} bar'
            )

            plt.savefig(os.path.join(self.output_dir, f"jet_test_{index + 1}.png"))
            plt.close(fig)

    def test_water_jet_visuals(self):
        """
        Generate and save 3D visuals for various water jet configurations
        """
        max_heights = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]  # meters
        vertical_angles = [15, 20, 25, 30, 35, 45, 50, 55, 60, 65, 70, 75]  # degrees
        horizontal_angles = [
            0,
            15,
            30,
            45,
            60,
            75,
            90,
            105,
            120,
            135,
            150,
            165,
            180,
        ]  # degrees

        for max_height in max_heights:
            self.hose.calibrate(
                max_distance=self.hose.max_distance,
                max_height=max_height,
                flow_rate=self.hose.flow_rate,
            )
            self._generate_height_plot(self.hose, vertical_angles, horizontal_angles)

    def _generate_height_plot(self, hose: Hose, vertical_angles, horizontal_angles):
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection="3d")

        for v_angle in vertical_angles:
            for h_angle in horizontal_angles:
                wj = WaterJet(start_position=Point3D(0, 0, 1), hose=hose)
                wj.set_angles(horizontal_angle=h_angle, vertical_angle=v_angle)
                trajectory = wj.calculate_trajectory()

                # Plot the trajectory
                x, y, z = zip(*[(p.x, p.y, p.z) for p in trajectory])
                ax.plot(x, y, z, label=f"V-Angle: {v_angle}°, H-Angle: {h_angle}°")

        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_zlabel("Z (m)")
        ax.set_title(f"Water Jet Trajectories (Max Height: {hose.max_height} m)")
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()

        plt.savefig(
            os.path.join(self.output_dir, f"jet_max_height_{hose.max_height}.png")
        )
        plt.close(fig)

        self._print_jet_stats(hose, vertical_angles, horizontal_angles)

    def _print_jet_stats(self, hose: Hose, vertical_angles, horizontal_angles):
        print(f"\nMax Height: {hose.max_height} m")
        print("-----------------------------")
        for v_angle in vertical_angles:
            for h_angle in horizontal_angles:
                wj = WaterJet(start_position=Point3D(0, 0, 1), hose=hose)
                wj.set_angles(horizontal_angle=h_angle, vertical_angle=v_angle)
                trajectory = wj.calculate_trajectory()

                max_height = max(p.z for p in trajectory)
                max_distance = max(math.sqrt(p.x**2 + p.y**2) for p in trajectory)

                print(f"V-Angle: {v_angle}°, H-Angle: {h_angle}°")
                print(f"  Max Height: {max_height:.2f}m")
                print(f"  Max Distance: {max_distance:.2f}m")
