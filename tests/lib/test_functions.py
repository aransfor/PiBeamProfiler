"""
Test functions.py module
"""
import unittest as ut
import pi_beam_profiler.lib.functions as functions
import numpy as np


class TestMath(ut.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__gaussian(self):
        x = 2.
        a = 1.
        x0 = 0.
        w_I = 3.
        expect = functions._gaussian(x, a, x0, w_I)
        value = 0.641180388
        self.assertAlmostEqual(expect, value, places=7)

    def test_fit_gaussian(self):
        a_guess = 1.
        x0_guess = 0.
        w_I_guess = 3.
        positions = np.linspace(-5, 5, 501)
        _amplitudes = functions._gaussian(
            positions, a_guess, x0_guess, w_I_guess)

        noises = np.array([np.random.rand()*.001 for kk in _amplitudes])
        amplitudes = _amplitudes + noises
        a, x0, w_I = functions.fit_gaussian(
            positions, amplitudes, a_guess, x0_guess, w_I_guess)

        self.assertAlmostEquals(a, a_guess, places=2)
        self.assertAlmostEquals(x0, x0_guess, places=2)
        self.assertAlmostEquals(w_I, w_I_guess, places=2)

    def test__sort_two_lists(self):
        l1 = [3, 1, 4, 2]
        l2 = [10, 20, 30, 40]
        sorted_l1, sorted_l2 = functions._sort_two_lists(l1, l2)
        expect_l1 = [1, 2, 3, 4]
        expect_l2 = [20, 40, 10, 30]
        self.assertSequenceEqual([sorted_l1, sorted_l2],
                                 [expect_l1, expect_l2])

    def test_coarsen_no_xdata(self):
        ydata = [1, 2, 3, 4]
        expect = [1.5, 3.5]
        value = functions.coarsen(ydata=ydata, points=2)
        self.assertListEqual(expect, value)

    def test_coarsen_with_xdata(self):
        ydata = [1, 2, 3, 4]
        xdata = [0, 2, 1, 3]
        coarsened_ydata, coarsened_xdata = functions.coarsen(ydata, xdata, 2)
        expect_ydata = [2, 3]
        expect_xdata = [1, 3]
        self.assertSequenceEqual([coarsened_ydata, coarsened_xdata],
                                 [expect_ydata, expect_xdata])
