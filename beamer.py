"""example script for profiling a beam; starts with a preview and will measure 100 times, roughly 3 seconds per measurement"""

import MT_g2d as g2d
from beam_profiler_XP import BeamProfiler as bp
import numpy as np
import sys as sys

if (len(sys.argv) != 3):
#	Check for correct arguments and print out help
	print "ERROR! Incorrect arguments"
	print "run beamer.py shutter iso"
	print "shutter -> time in milliseconds"
	print "iso = 0-1600 (0 = auto)"
	sys.exit()

#	Take in two arguments: shutter, iso
str_shutter = str(sys.argv[1])
str_iso = str(sys.argv[2])

#	Convert the argument strings into ints
shutter = int(str_shutter)
iso = int(str_iso)

#	Make the beam profiler object
beamProfiler=bp()

for i in range (0,1):
	"""Preview, and take image"""
	beamProfiler.take_image_preview(shutter, iso)

	"""Find max"""
	pixel_max = np.amax(beamProfiler.pixel_array)
	print 'pixel max = ', pixel_max

	"""Fit image data to Gaussian"""
	Gauss2D = g2d.Gaussian2D(beamProfiler.pixel_array)

	"""Print widths of fit"""
	print 'w_a_pix = ', Gauss2D._w_a_pix, 'pixels'
	print 'w_b_pix = ', Gauss2D._w_b_pix, 'pixels'
	print 'w_a_len = ', Gauss2D._w_a_len, 'mm'
	print 'w_b_len = ', Gauss2D._w_b_len, 'mm'
	
	i = i+1
