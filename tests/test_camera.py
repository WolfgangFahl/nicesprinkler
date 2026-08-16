"""
Created on 2026-08-16

@author: wf
"""

import io
import os

from basemkit.basetest import Basetest
from PIL import Image

from sprinkler.camera import Camera


class TestCamera(Basetest):
    """
    test the camera frame handling
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        images = os.path.join(os.path.dirname(__file__), "..", "images")
        self.jpeg_path = os.path.abspath(
            os.path.join(images, "20260816_085040_00203_devcam.jpg")
        )

    def test_exif_orientation(self):
        """
        test that the configured rotation is served as an exif orientation
        and that no pixel is touched by it
        """
        raw = open(self.jpeg_path, "rb").read()
        expected = {0: None, 90: 6, 180: 3, 270: 8}
        for rotation, orientation in expected.items():
            camera = Camera(rotation=rotation)
            oriented = camera.oriented(raw)
            image = Image.open(io.BytesIO(oriented))
            if self.debug:
                print(f"{rotation}°: {image.getexif().get(274)} {image.size}")
            self.assertEqual(orientation, image.getexif().get(274))
            self.assertEqual((1600, 896), image.size)
