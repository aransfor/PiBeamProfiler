"""
Test camera_image.py module

Preparation of the 2D gaussian data is taken from the following link:

http://stackoverflow.com/questions/21566379/
fitting-a-2d-gaussian-function-using-scipy-optimize-curve-fit-valueerror-and-m
"""
import unittest as ut
import pi_beam_profiler.lib.camera_image as _ci
import numpy as np


class TestMath(ut.TestCase):
    def setUp(self):
        image = self._prepare_image()
        self.camera_image = _ci.CameraImage(image=image)

    def tearDown(self):
        self.camera_image = None

    def test_row_values(self):
        row_amp = self.camera_image.row_amp
        row_center = self.camera_image.row_center
        row_width = self.camera_image.row_width
        exp_row_amp = 3.988021164
        exp_row_center = 300.
        exp_row_width = 50.
        self.assertAlmostEquals(row_center, exp_row_center)
        self.assertAlmostEquals(row_width, exp_row_width)
        self.assertAlmostEquals(row_amp, exp_row_amp)

    def test_column_values(self):
        column_amp = self.camera_image.column_amp
        column_center = self.camera_image.column_center
        column_width = self.camera_image.column_width
        exp_column_amp = 6.64670194
        exp_column_center = 300.
        exp_column_width = 30.
        self.assertAlmostEquals(column_center, exp_column_center)
        self.assertAlmostEquals(column_width, exp_column_width)
        self.assertAlmostEquals(column_amp, exp_column_amp)

    def _prepare_image(self):
        x = np.linspace(0, 600, 601)
        y = np.linspace(0, 600, 601)
        x, y = np.meshgrid(x, y)
        data = self._twoD_Gaussian((x, y), 3, 300, 300, 30, 50)
        image = data.reshape(601, 601)
        return image

    def _twoD_Gaussian(self, (x, y), amplitude, xo, yo, sigma_x, sigma_y):
        xo = float(xo)
        yo = float(yo)
        a = 1./(sigma_x**2)
        c = 1./(sigma_y**2)
        g = amplitude*np.exp(-(a*((x-xo)**2) + c*((y-yo)**2)))
        return g.ravel()
