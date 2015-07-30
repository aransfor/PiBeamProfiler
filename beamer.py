import XP_g2d as g2d
from beam_profiler_XP import BeamProfiler as bp
from matplotlib import pylab as pylab

"""
These will be givin user input capabilities later on
shutter = the speed of the shutter (in ms?)
a_res = the resolution in the x
b_res = the resolution in the y
"""
#The guessing values depend in some way on a_res and b_res, at least as limits
shutter = 2000
a_res = 100
b_res = 100

b=bp()
b.take_image(a_res, b_res, shutter)
#b.image.show()

G2D = g2d.Gaussian2D(b.array, rho=50, x0=30, y0=20, w_a=9, w_b=7)
print 'w_a = ', G2D.w_a_len, 'm'
print 'w_b = ', G2D.w_b_len, 'm'


"""
Graphs the gaussian fits in the x and y directions
''
row_sum = [sum(b.array[:,i]) for i in xrange(len(b.array[0]))]
col_sum = [sum(b.array[i,:]) for i in xrange(len(b.array[1]))]
pylab.plot(row_sum)
pylab.plot(col_sum)
pylab.show()
"""
