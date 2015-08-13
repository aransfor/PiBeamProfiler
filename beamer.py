import XP_g2d as g2d
from beam_profiler_XP import BeamProfiler as bp
from matplotlib import pylab as pylab
import numpy as np

b=bp()
b.see_preview()
shutter_cal = b.calibrate_shutter_simple()
b.take_image()
max_pix = np.amax(b.array)
b.image.show()

G2D = g2d.Gaussian2D(b.array, rho=50, x0=30, y0=20, w_a=9, w_b=7)
print 'w_a = ', G2D.w_a_len, 'mm'
print 'w_b = ', G2D.w_b_len, 'mm'
print 'max_pix = ', max_pix 


"""
Graphs the gaussian fits in the x and y directions
''
row_sum = [sum(b.array[:,i]) for i in xrange(len(b.array[0]))]
col_sum = [sum(b.array[i,:]) for i in xrange(len(b.array[1]))]
pylab.plot(row_sum)
pylab.plot(col_sum)
pylab.show()
"""
