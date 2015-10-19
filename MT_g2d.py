# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 22:22:32 2015
@author: XP
Modified on Tue Oct 12
@author: MT
"""
import numpy as _n
from scipy.optimize import curve_fit as _curve_fit


class Gaussian2D(object):
    """
    2D Gaussian class
    """
    def __init__(self, data):
	"""Values generated as result of fit"""
	self._x0 = None  # center column
        self._y0 = None  # center row
        self._w_a = None  # long axis length in pixels
        self._w_b = None  # short axis length in pixels
        self._rho = None  # amplitude of 2D Gaussian
	
	"""Initial guesses required for the fitting"""
        self._x0_g = 50  # center column
        self._y0_g = 30  # center row
        self._w_a_g = 20  # long axis length in pixels
        self._w_b_g = 9  # short axis length in pixels
        self._rho_g = 7  # amplitude of 2D Gaussian

	"""Error produced required for the fitting"""
        self._x0_err = None
        self._y0_err = None
        self._w_a_err = None
        self._w_b_err = None
        self._rho_err = None

	"""Values for the user as a result of the fitting"""
	self._x0_pos = None
	self._y0_pos = None
	self._w_a_len = None
	self._w_b_len = None

	"""Values based on resolution of image"""
	self._pixel_size = 0.0000014
	self._a_pixel_len = 2592
	self._b_pixel_len = 1944
	self._pixel_res = 100

        if data is None:
            print "Please load data."
            return
        self._data = data
        self._fit_2DGaussian()

    def _fit_2DGaussian(self):
        initial_guess = (self._rho_g, self._x0_g, self._y0_g, self._w_a_g, self._w_b_g)

        """Get the row & column numbers"""
        row_num = len(self._data)
        col_num = len(self._data[0])

        """Create x and y indices"""
        x = _n.linspace(0, col_num-1, col_num)
        y = _n.linspace(0, row_num-1, row_num)
        x, y = _n.meshgrid(x, y)

        """The fitting"""
        popt, pcov = _curve_fit(self._twoD_Gaussian, (x, y),
                                    self._data.flatten(), p0=initial_guess)
        """Return the fitting parameter results, and convert the positions and lengths to millimeters"""
        self._rho = popt[0]
        self._x0 = popt[1]
        self._y0 = popt[2]
        self._w_a = abs(popt[3])
        self._w_b = abs(popt[4])
        self._rho_err = _n.sqrt(pcov[0][0])
        self._x0_err = _n.sqrt(pcov[1][1])
        self._y0_err = _n.sqrt(pcov[2][2])
        self._w_a_err = _n.sqrt(pcov[3][3])
        self._w_b_err = _n.sqrt(pcov[4][4])

	#self._x0_pos = 25.92 * self._pixel_size * self._x0 * 1000
	#self._y0_pos = 19.44 * self._pixel_size * self._y0 * 1000
	self._w_a_len = 25.92 * self._pixel_size * self._w_a * 1000
	self._w_b_len = 19.44 * self._pixel_size * self._w_b * 1000

    def _twoD_Gaussian(self, (x, y), rho, x0, y0, w_a, w_b):
        """
        Define the 2D guassian function that we're trying to fit to.
        Parameters
        ----------
        (x,y): tuple of index matrices. It's generated in _fit_2DGaussian(self)
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
