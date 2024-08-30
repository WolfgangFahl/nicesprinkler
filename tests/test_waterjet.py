"""
Created on 2024-08-29

@author: wf
"""

import math
import os

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from ngwidgets.basetest import Basetest

from sprinkler.waterjet import JetParams, JetSpline, Point3D, WaterJet


class TestWaterjetVisual(Basetest):
    """
    Visual tests for Waterjet functionality
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.output_dir = "/tmp/waterjet_test"
        os.makedirs(self.output_dir, exist_ok=True)

    def test_water_jet(self):
        """
        Test the water jet calculations
        """
        jet_params = JetParams(
            start_position=Point3D(0, 0, 1),
            horizontal_angle=45,
            vertical_angle=30,
        )
        wj = WaterJet(jet_params=jet_params)
        jet_spline = wj.calculate_jet()

        self.assertIsInstance(jet_spline, JetSpline)
        self.assertEqual(jet_spline.start, jet_params.start_position)
        self.assertGreater(jet_spline.control1.z, jet_params.start_position.z)
        self.assertGreater(jet_spline.control2.z, 0)
        self.assertEqual(jet_spline.end.z, 0)

    def test_water_jet_visuals(self):
        """
        Generate and save 3D visuals for various water jet configurations
        """
        pressures = [0.2, 0.3, 0.4, 0.6, 0.8]  # bar (more realistic for garden tap)
        vertical_angles = [15, 20, 25, 30, 35, 45, 50]  # degrees
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

        for pressure in pressures:
            self._generate_pressure_plot(pressure, vertical_angles, horizontal_angles)

    def _generate_pressure_plot(self, pressure, vertical_angles, horizontal_angles):
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection="3d")

        for v_angle in vertical_angles:
            for h_angle in horizontal_angles:
                jet_params = JetParams(
                    start_position=Point3D(0, 0, 1),
                    horizontal_angle=h_angle,
                    vertical_angle=v_angle,
                    pressure=pressure,
                )
                wj = WaterJet(jet_params=jet_params)
                jet_spline = wj.calculate_jet()

                # Plot the spline
                t = np.linspace(0, 1, 100)
                points = jet_spline.evaluate_spline(t)
                x, y, z = zip(*points)
                ax.plot(x, y, z, label=f"V-Angle: {v_angle}°, H-Angle: {h_angle}°")

        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_zlabel("Z (m)")
        ax.set_title(f"Water Jet Trajectories (Pressure: {pressure} bar)")
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()

        plt.savefig(os.path.join(self.output_dir, f"jet_pressure_{pressure}.png"))
        plt.close(fig)

        self._print_jet_stats(pressure, vertical_angles, horizontal_angles)

    def _print_jet_stats(self, pressure, vertical_angles, horizontal_angles):
        print(f"\nPressure: {pressure} bar")
        print("-----------------------------")
        for v_angle in vertical_angles:
            for h_angle in horizontal_angles:
                jet_params = JetParams(
                    start_position=Point3D(0, 0, 1),
                    horizontal_angle=h_angle,
                    vertical_angle=v_angle,
                    pressure=pressure,
                )
                wj = WaterJet(jet_params=jet_params)
                jet_spline = wj.calculate_jet()

                t = np.linspace(0, 1, 100)
                points = jet_spline.evaluate_spline(t)
                max_height = max(p[2] for p in points)
                max_distance = math.sqrt(
                    (jet_spline.end.x - jet_spline.start.x) ** 2
                    + (jet_spline.end.y - jet_spline.start.y) ** 2
                )

                print(f"V-Angle: {v_angle}°, H-Angle: {h_angle}°")
                print(f"  Max Height: {max_height:.2f}m")
                print(f"  Max Distance: {max_distance:.2f}m")
