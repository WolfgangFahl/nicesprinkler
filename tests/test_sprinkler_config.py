"""
Created on 2024-09-03

@author: wf
"""

import json

from sprinkler.sprinkler_config import (
    AngleRange,
    Angles,
    Hose,
    Lawn,
    Motor,
    Motors,
    SprinklerConfig,
    SprinklerHead,
)
from tests.sprinkler_base_test import SprinklerBasetest


class TestSprinklerConfig(SprinklerBasetest):
    """
    test sprinkler configuration
    """

    def setUp(self, debug=True, profile=True):
        SprinklerBasetest.setUp(self, debug=debug, profile=profile)

    def test_hose(self):
        """
        test the hose calibration
        """
        hose = Hose()
        hose.calibrate(7.4, 3.35, 12 / (63 / 60))
        if self.debug:
            print(hose.specs())

    def test_config_loading(self):
        """Test loading the sprinkler configuration"""
        self.assertIsInstance(self.config, SprinklerConfig)
        if self.debug:
            for part in [
                self.config.lawn,
                self.config.sprinkler_head,
                self.config.angles.horizontal,
                self.config.angles.vertical,
                self.config.hose,
                self.config.motors,
            ]:
                print(json.dumps(part, indent=2, default=str))
            print(self.config.hose.specs())

        # Assert the lawn configuration
        self.assertIsInstance(self.config.lawn, Lawn)
        self.assertAlmostEqual(self.config.lawn.width, 6.1)
        self.assertAlmostEqual(self.config.lawn.length, 14.6)
        self.assertAlmostEqual(self.config.lawn.area, 89.06)

        # Assert the sprinkler head configuration
        self.assertIsInstance(self.config.sprinkler_head, SprinklerHead)
        self.assertAlmostEqual(self.config.sprinkler_head.x, 3.05)
        self.assertAlmostEqual(self.config.sprinkler_head.y, 0.0)
        self.assertAlmostEqual(self.config.sprinkler_head.z, 1.2)

        # Assert the angles configuration
        self.assertIsInstance(self.config.angles, Angles)
        self.assertIsInstance(self.config.angles.horizontal, AngleRange)
        self.assertIsInstance(self.config.angles.vertical, AngleRange)

        # Horizontal angle range assertions
        self.assertAlmostEqual(self.config.angles.horizontal.min, -85.0)
        self.assertAlmostEqual(self.config.angles.horizontal.max, 85.0)
        self.assertAlmostEqual(self.config.angles.horizontal.initial, 0.0)
        self.assertAlmostEqual(self.config.angles.horizontal.step, 2.0)
        self.assertListEqual(
            self.config.angles.horizontal.angles,
            [
                -85.0,
                -83.0,
                -81.0,
                -79.0,
                -77.0,
                -75.0,
                -73.0,
                -71.0,
                -69.0,
                -67.0,
                -65.0,
                -63.0,
                -61.0,
                -59.0,
                -57.0,
                -55.0,
                -53.0,
                -51.0,
                -49.0,
                -47.0,
                -45.0,
                -43.0,
                -41.0,
                -39.0,
                -37.0,
                -35.0,
                -33.0,
                -31.0,
                -29.0,
                -27.0,
                -25.0,
                -23.0,
                -21.0,
                -19.0,
                -17.0,
                -15.0,
                -13.0,
                -11.0,
                -9.0,
                -7.0,
                -5.0,
                -3.0,
                -1.0,
                1.0,
                3.0,
                5.0,
                7.0,
                9.0,
                11.0,
                13.0,
                15.0,
                17.0,
                19.0,
                21.0,
                23.0,
                25.0,
                27.0,
                29.0,
                31.0,
                33.0,
                35.0,
                37.0,
                39.0,
                41.0,
                43.0,
                45.0,
                47.0,
                49.0,
                51.0,
                53.0,
                55.0,
                57.0,
                59.0,
                61.0,
                63.0,
                65.0,
                67.0,
                69.0,
                71.0,
                73.0,
                75.0,
                77.0,
                79.0,
                81.0,
                83.0,
                85.0,
            ],
        )

        # Vertical angle range assertions
        self.assertAlmostEqual(self.config.angles.vertical.min, -75.0)
        self.assertAlmostEqual(self.config.angles.vertical.max, 75.0)
        self.assertAlmostEqual(self.config.angles.vertical.initial, 0.0)
        self.assertAlmostEqual(self.config.angles.vertical.step, 2.0)
        self.assertListEqual(
            self.config.angles.vertical.angles,
            [
                -75.0,
                -73.0,
                -71.0,
                -69.0,
                -67.0,
                -65.0,
                -63.0,
                -61.0,
                -59.0,
                -57.0,
                -55.0,
                -53.0,
                -51.0,
                -49.0,
                -47.0,
                -45.0,
                -43.0,
                -41.0,
                -39.0,
                -37.0,
                -35.0,
                -33.0,
                -31.0,
                -29.0,
                -27.0,
                -25.0,
                -23.0,
                -21.0,
                -19.0,
                -17.0,
                -15.0,
                -13.0,
                -11.0,
                -9.0,
                -7.0,
                -5.0,
                -3.0,
                -1.0,
                1.0,
                3.0,
                5.0,
                7.0,
                9.0,
                11.0,
                13.0,
                15.0,
                17.0,
                19.0,
                21.0,
                23.0,
                25.0,
                27.0,
                29.0,
                31.0,
                33.0,
                35.0,
                37.0,
                39.0,
                41.0,
                43.0,
                45.0,
                47.0,
                49.0,
                51.0,
                53.0,
                55.0,
                57.0,
                59.0,
                61.0,
                63.0,
                65.0,
                67.0,
                69.0,
                71.0,
                73.0,
                75.0,
            ],
        )

        # Assert the hose configuration
        self.assertIsInstance(self.config.hose, Hose)
        self.assertAlmostEqual(self.config.hose.diameter, 12.7)
        self.assertAlmostEqual(self.config.hose.flow_rate, 20.0)
        self.assertAlmostEqual(self.config.hose.pressure, 0.5586)
        self.assertAlmostEqual(self.config.hose.velocity, 10.57, 2)
        self.assertAlmostEqual(self.config.hose.nozzle_area, 31.54, 2)
        self.assertAlmostEqual(self.config.hose.max_distance, 13.6)

        # Assert the motors configuration
        self.assertIsInstance(self.config.motors, Motors)
        self.assertIsInstance(self.config.motors.horizontal, Motor)
        self.assertIsInstance(self.config.motors.vertical, Motor)

        # Horizontal motor assertions
        self.assertEqual(self.config.motors.horizontal.ena_pin, 37)
        self.assertEqual(self.config.motors.horizontal.dir_pin, 35)
        self.assertEqual(self.config.motors.horizontal.pul_pin, 33)
        self.assertEqual(self.config.motors.horizontal.steps_per_revolution, 200)
        self.assertEqual(self.config.motors.horizontal.min_angle, -90)
        self.assertEqual(self.config.motors.horizontal.max_angle, 90)

        # Vertical motor assertions
        self.assertEqual(self.config.motors.vertical.ena_pin, 31)
        self.assertEqual(self.config.motors.vertical.dir_pin, 29)
        self.assertEqual(self.config.motors.vertical.pul_pin, 23)
        self.assertEqual(self.config.motors.vertical.steps_per_revolution, 200)
        self.assertEqual(self.config.motors.vertical.min_angle, 0)
        self.assertEqual(self.config.motors.vertical.max_angle, 60)

        # If debug mode is on, print the config details
        if self.debug:
            for part in [
                self.config.lawn,
                self.config.sprinkler_head,
                self.config.angles.horizontal,
                self.config.angles.vertical,
                self.config.hose,
                self.config.motors,
            ]:
                print(json.dumps(part, indent=2, default=str))
