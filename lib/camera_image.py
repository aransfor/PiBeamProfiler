"""
Class to hold row and column sum data, projections of the image.
"""
import numpy as _n
# import cv2 as _cv2
import functions as _functions


class CameraImage(object):
    """ Processed single image taken by the pi-camera. """
    def __init__(self, image, coarsen=False):
        self.image = image
        self.coarsen = coarsen

        self._global_max = _n.max(self.image)
        self.saturation = self._global_max / 255. * 100.
        self._scale_factor = 40.
        self._beam_diameter_guess = 200.

        self._process_image()

    def _process_image(self):
        self._calculate_column_and_row_sums()
        if self.coarsen:
            self._coarsen()
        self._make_guesses()
        self._gaussian_fit_column_and_row_sums()

    def _calculate_column_and_row_sums(self):
        inverted_row_sum = self.image.sum(axis=1)/self._scale_factor

        column_sum = self.image.sum(axis=0)/self._scale_factor

        # background substraction
        self.column_sum = column_sum - _n.min(column_sum)
        inverted_row_sum = inverted_row_sum - _n.min(inverted_row_sum)
        self.row_sum = inverted_row_sum[::-1]

        self.column_positions = range(len(self.column_sum))
        self.row_positions = range(len(self.row_sum))

    def _coarsen(self):
        self._coarsen_factor = 3.
        # TODO: add coarsen functionality if necessary
        pass

    def _make_guesses(self):
        self._column_amp_guess = self.column_sum.max()
        self._column_center_guess = _n.argmax(self.column_sum)
        self._row_amp_guess = self.row_sum.max()
        self._row_center_guess = _n.argmax(self.row_sum)

    def _gaussian_fit_column_and_row_sums(self):
        column_fit = _functions.fit_gaussian(
            self.column_positions, self.column_sum, self._column_amp_guess,
            self._column_center_guess, self._beam_diameter_guess)

        self.column_amp, self.column_center, self.column_width = column_fit
        self.column_sum_fit = _functions._gaussian(
            _n.array(self.column_positions), *column_fit)

        row_fit = _functions.fit_gaussian(
            self.row_positions, self.row_sum, self._row_amp_guess,
            self._row_center_guess, self._beam_diameter_guess)

        self.row_amp, self.row_center, self.row_width = row_fit
        self.row_sum_fit = _functions._gaussian(
            _n.array(self.row_positions), *row_fit)
