import numpy as _n
from scipy.optimize import curve_fit as _curve_fit


def _gaussian(x, a, x0, w_I):
    """ A Gaussian profile function used in fitting routine.

    Parameters
    ----------
    x: float, abscissa
    a: float, amplitude coefficient
    x0: float, center
    w_I: float, 1/e intensity radius in pixels

    Returns
    -------
    float
    """
    return a*_n.exp(-(x-x0)**2/(w_I**2))


def fit_gaussian(positions, amplitudes, a_guess, x0_guess, w_I_guess=200):
    """ Return result from a gaussian fit.

    Parameters
    ----------
    positions: list of float, positions on a gaussian curve
    amplitudes: list of float, amplitudes on a gaussian curve
    a_guess: float, guessed peak amplitude of the gaussian
    x0_guess: float, guessed center position of the gaussian
    w_I_guess: float, guessed 1/e intensity radius in pixels

    Returns
    -------
    a: float, peak amplitude of the gaussian from fit result
    x0: float, center position of the gaussian from fit result
    w_I: float, 1/e intensity radius in pixels from fit result
    """
    # guessed parameters that gets sent into the curve_fit function
    p0 = [a_guess, x0_guess, w_I_guess]
    try:
        popt, pcov = _curve_fit(_gaussian, positions, amplitudes, p0=p0)
    # TODO: replace the following with a real excetion, rather than a general
    # except
    except:
        # if a fit cannot be obtained, return [0, 0, 1] for a, x0 and w_I
        popt = [0, 0, 1]
    a, x0, w_I = popt
    return a, x0, w_I


def coarsen(ydata, xdata=None, points=3):
    """ Return coarsened data

    Parameters
    ----------
    ydata: list of float, data to be coarsened
    points: int, how many points to coarsen
    xdata: list of float, position corresponding to the ydata. This is optional

    Return(s)
    ---------
    coarsened_ydata: list of float, coarsened data
    coarsened_xdata: list of float, position of coarsened data if xdata is not
        None. Otherwise this is not returned.
    """
    newlength = int(len(ydata)/points)
    if xdata is None:
        coarsened_ydata = [_n.mean(ydata[kk * points: kk * points + points])
                           for kk in xrange(newlength)]
        return coarsened_ydata

    sorted_xdata, sorted_ydata = _sort_two_lists(xdata, ydata)
    coarsened_ydata = [_n.mean(sorted_ydata[kk * points: kk * points + points])
                       for kk in xrange(newlength)]
    coarsened_xdata = [
        sorted_xdata[int((kk * points + (kk * points + points))/2)] for kk in
        xrange(newlength)]
    return coarsened_ydata, coarsened_xdata


def _sort_two_lists(xdata, ydata):
    """ Simultaneously sort two lists based on the first list.

    Example: list1 = [3, 1, 4, 2], list2 = [10, 20, 30, 40], this function
    returns sorted_list1 = [1, 2, 3, 4], sorted_list2 = [20, 40, 10, 30].

    Parameters
    ----------
    xdata: list of float
    ydata: list of float

    Returns
    -------
    sorted_xdata: list of float
    sorted_ydata: list of float
    """
    sorted_tuple_list = sorted(zip(xdata, ydata))
    sorted_xdata = [_tuple[0] for _tuple in sorted_tuple_list]
    sorted_ydata = [_tuple[1] for _tuple in sorted_tuple_list]
    return sorted_xdata, sorted_ydata
