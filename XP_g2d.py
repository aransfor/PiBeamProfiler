#test
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 22:22:32 2015
@author: XP
"""
import numpy as _n
from scipy.optimize import curve_fit as _curve_fit


class Gaussian2D(object):
    """
    2D Gaussian class
    """
    def __init__(self, data, **kwargs):
        self.x0 = None  # center column
        self.y0 = None  # center row
        self.w_a = None  # long axis length in pixels
        self.w_b = None  # short axis length in pixels
        self.rho = None  # amplitude of 2D Gaussian
        self.x0_err = None
        self.y0_err = None
        self.w_a_err = None
        self.w_b_err = None
        self.rho_err = None
	self.w_a_len = None
	self.w_b_len = None

	self.pixel_size = 0.0000014
	self.a_pixel_len = 2592
	self.b_pixel_len = 1944

        if data is None:
            print "Please load data."
            return
        self.data = data
        self._fit_2DGaussian(**kwargs)

    def _fit_2DGaussian(self, **kwargs):
        """
        2D guassian fit function. XP found this code online from
        http://stackoverflow.com/questions/21566379/fitting-a-2d-gaussian-function-using-scipy-optimize-curve-fit-valueerror-and-m
        Parameters
        ----------
        kwargs
        ------
        rho: float32, the initial guess for amplitude of the gaussian. default(0.3)
        x0: int, the initial guess for the column of the peak in pixels. default(300)
        y0: int, the initial guess for the row of the peak in pixels. default(250)
        w_a: float32, the initial guess for the bigger standard deviation. default(25)
        w_b: float32, the initial guess for the smaller standard deviation. default(20)
        Background: float32, the initial guess for the offset. default(0.02)
        plot: boolean, whether the resultant fit should be plotted. default(False)
        """
        rho = kwargs['rho']
        x0 = kwargs['x0']
        y0 = kwargs['y0']
        w_a = kwargs['w_a']
        w_b = kwargs['w_b']
        initial_guess = (rho, x0, y0, w_a, w_b)

        # Get the row & column numbers
        row_num = len(self.data)
        col_num = len(self.data[0])

        # Create x and y indices
        x = _n.linspace(0, col_num-1, col_num)
        y = _n.linspace(0, row_num-1, row_num)
        x, y = _n.meshgrid(x, y)

        # The fitting
        popt, pcov = _curve_fit(self._twoD_Gaussian, (x, y),
                                    self.data.flatten(), p0=initial_guess)
        # Return the fitting parameter results, and convert the position to meters.
        self.rho = popt[0]
        self.x0 = popt[1]
        self.y0 = popt[2]
        self.w_a = abs(popt[3])
        self.w_b = abs(popt[4])
        self.rho_err = _n.sqrt(pcov[0][0])
        self.x0_err = _n.sqrt(pcov[1][1])
        self.y0_err = _n.sqrt(pcov[2][2])
        self.w_a_err = _n.sqrt(pcov[3][3])
        self.w_b_err = _n.sqrt(pcov[4][4])

	self.w_a_len = 100 * self.pixel_size * self.w_a
	self.w_b_len = 100 * self.pixel_size * self.w_b

    def _twoD_Gaussian(self, (x, y), rho, x0, y0, w_a, w_b):
        """
        Define the 2D guassian function that we're trying to fit to.
        Parameters
        ----------
        (x,y): tuple of index matrices. It's generated in gaussian2D_fit(image_array, **kwargs)
        rho: the initial guess for amplitude of the gaussian
        x0: the column of the peak in pixels
        y0: the initial guess for the row of the peak in pixels
        w_a: the initial guess for the bigger standard deviation
        w_b: the initial guess for the smaller standard deviation
        """
        x0 = float(x0)
        y0 = float(y0)
        a = 1./(2*w_a**2)
        c = 1./(2*w_b**2)
        g = rho*_n.exp( - (a*((x-x0)**2) + c*((y-y0)**2)))
        return g.ravel()
