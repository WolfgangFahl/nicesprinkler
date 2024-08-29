"""
Created on 2024-08-29

@author: wf
"""
import os
import math
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from ngwidgets.basetest import Basetest
from sprinkler.waterjet import WaterJet, Point3D, JetParams, JetSpline

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
        test the water jet calculations
        """
        jet_params = JetParams(
        start_position=Point3D(0, 0, 1),
        horizontal_angle=45,
        vertical_angle=30,
        )
        wj=WaterJet(jet_params=jet_params)

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
        pressures = [0.5, 1.0, 1.5]  # bar
        vertical_angles = [15, 30, 45]  # degrees
        horizontal_angles = [0, 45, 90]  # degrees

        for pressure in pressures:
            for v_angle in vertical_angles:
                for h_angle in horizontal_angles:
                    self.generate_jet_visual(pressure, v_angle, h_angle)

    def generate_jet_visual(self, pressure, v_angle, h_angle):
        jet_params = JetParams(
            start_position=Point3D(0, 0, 1),
            horizontal_angle=h_angle,
            vertical_angle=v_angle,
            pressure=pressure
        )
        wj = WaterJet(jet_params=jet_params)
        jet_spline = wj.calculate_jet()

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Plot the spline
        t = np.linspace(0, 1, 100)
        points = self.evaluate_spline(jet_spline, t)
        x, y, z = zip(*points)
        ax.plot(x, y, z, label='Water Jet')

        # Plot control points
        control_points = [jet_spline.start, jet_spline.control1, jet_spline.control2, jet_spline.end]
        x, y, z = zip(*[p.to_tuple() for p in control_points])
        ax.scatter(x, y, z, color='red', s=50, label='Control Points')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Water Jet (Pressure: {pressure}bar, V-Angle: {v_angle}°, H-Angle: {h_angle}°)')
        ax.legend()

        plt.savefig(os.path.join(self.output_dir, f'jet_p{pressure}_v{v_angle}_h{h_angle}.png'))
        plt.close(fig)

        # Perform some checks
        self.assertEqual(jet_spline.start, jet_params.start_position)
        self.assertGreater(jet_spline.control1.z, jet_params.start_position.z)
        self.assertGreater(jet_spline.control2.z, 0)
        self.assertEqual(jet_spline.end.z, 0)

        # Additional checks
        max_height = max(p[2] for p in points)
        max_distance = math.sqrt((jet_spline.end.x - jet_spline.start.x)**2 +
                                 (jet_spline.end.y - jet_spline.start.y)**2)

        print(f"Configuration: Pressure={pressure}bar, V-Angle={v_angle}°, H-Angle={h_angle}°")
        print(f"Max Height: {max_height:.2f}m")
        print(f"Max Distance: {max_distance:.2f}m")
        print("-----------------------------")

    def evaluate_spline(self, spline: JetSpline, t):
        """Evaluate the Bezier spline at the given parameter values."""
        points = []
        for ti in t:
            p = (1-ti)**3 * spline.start + \
                3*(1-ti)**2*ti * spline.control1 + \
                3*(1-ti)*ti**2 * spline.control2 + \
                ti**3 * spline.end
            points.append((p.x, p.y, p.z))
        return points
