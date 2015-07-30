from PyQt4 import QtGui
import sys
import os
import time
import urllib2
import numpy as np
import picamera
import picamera.array
import scipy.optimize as opt
from scipy.stats import norm
from matplotlib import pyplot as plt
from matplotlib import dates, ticker
import beam_profiler_XP as bp
import XP_g2d as g2d

class BeamProfiler(QtGui.QWidget):

	def __init__(self):
		super(BeamProfiler, self).__init__()
		self.image_data = bp()
		self.Gauss2D = None
		self._rho = 50
		self._x0 = 30
		self._y0 = 20
		self._w_a = 9
		self._w_b = 7
		self.row_sum = None
		self.col_sum = None
		self.initializeGUI()

	def initializeGUI(self):
		'''Initializes GUI
		'''
		self.setGeometry(400, 150, 350, 550)
		self.setWindowTitle('Beam Profiler')
		layout = QtGui.QGridLayout()
		from matplotlib import pyplot as plt
		captureFitImage  = QtGui.QPushButton('Capture and Fit Image')
		get1DnormX       = QtGui.QPushButton('Show a 1D Gaussian in the X')
		get1DnormY       = QtGui.QPushButton('Show a 1D Gaussian in the Y')
		getImage         = QtGui.QPushButton('Show the Image')
		getData          = QtGui.QPushButton('Show Gaussian Fit Data')
		#changeres        = QtGui.QPushButton('Change Resolution')
		
		captureFitImage.clicked.connect(self.capturefitimage)
		get1DnormX.clicked.connect(self.norm1D_x)
		get1DnormY.clicked.connect(self.norm1D_y)
		getImage.clicked.connect(self.image)
		getData.clicked.connect(self.data)
		#changeres.clicked.connect(self.changeres)
		
		layout.addWidget(captureFitImage    ,0,0)
		layout.addWidget(get1DnormX         ,1,0)
		layout.addWidget(get1DnormY         ,2,0)
		layout.addWidget(getImage           ,3,0)
		layout.addWidget(getData            ,4,0)
		#layout.addWidget(changeres          ,5,0)
		
		self.setLayout(layout)

	def capturefitimage(self):
		self.image_data.take_image(a_res, b_res, shutter)
		self.Gauss2D = g2d.Gaussian2D(self.image_date.array, rho=self._rho, x0=self._x0, y0=self._y0, _w_a=self._w_a, w_b=self._w_b)
		self.row_sum = [sum(self.image_data.array[:,i]) for i in xrange(len(self.image_data.array[0]))]
		self.col_sum = [sum(self.image_data.array[i,:]) for i in xrange(len(self.image_data.array[1]))]

	def norm1D_x(self):
		pylab.plot(self.row_sum)
		pylab.show()

	def norm1D_y(self):
		pylab.plot(self.col_sum)
		pylab.show()

	def image(self):
		self.image_data.image.show()

	def data(self):


if __name__ == "__main__":
    a = QtGui.QApplication([])
    beamWidget = BeamProfiler()
    beamWidget.show()
    sys.exit(a.exec_())
