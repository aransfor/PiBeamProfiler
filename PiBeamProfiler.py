#!/usr/bin/env python
# Copyright (C) 2015 Anthony Ransford
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL.ImageQt import ImageQt
from PyQt4 import QtGui, QtCore
import numpy as np
from scipy.misc.pilutil import toimage
from scipy.optimize import curve_fit
import time, sys
import cv2

class proflayout(QtGui.QWidget):

    def __init__(self):
        super(proflayout, self).__init__()
	self.zoom = 1
	self.imageres = [640,480]
	desktop = QtGui.QDesktopWidget()
	screensize = desktop.availableGeometry()
	print screensize
#	self.screenres = [800,480]
	self.screenres = [screensize.width(),screensize.height()]
	# initialize the camera
	self.camera = PiCamera()

	#set camera resolution, gain , sutter speed and framerate
	self.camera.resolution = (640, 480)
	self.camera.framerate = 33
	self.camera.shutter_speed = 500
	self.camera.exposure_mode = 'off'
	self.camera.iso = 300

	#grab a reference to the raw camera capture
	self.rawCapture = PiRGBArray(self.camera, size=(640, 480))

	# allow the camera to warmup
	time.sleep(0.1)
	self.initializeGUI()

    def initializeGUI(self):

        self.setWindowTitle('Beam Profiler')
	self.setGeometry(0, 0, self.screenres[0], self.screenres[1])
        layout = QtGui.QGridLayout()

	self.setupPlots()

	self.expslider = QtGui.QSlider(QtCore.Qt.Vertical)
	self.expslider.setSingleStep(1)
	self.explabel = QtGui.QLabel('Exposure')
	self.expbar = QtGui.QProgressBar()
	self.expbar.setOrientation(QtCore.Qt.Vertical)
	self.expbar.setValue(65)
	self.videowindow = QtGui.QLabel(self)

	self.xwaist = QtGui.QLabel()
	self.ywaist = QtGui.QLabel()
	self.xwaist.setStyleSheet('color: #FF6600; font-weight: bold; font-family: Copperplate / Copperplate Gothic Light, sans-serif') 
	self.ywaist.setStyleSheet('color: #FF6600; font-weight: bold; font-family: Copperplate / Copperplate Gothic Light, sans-serif')
	self.zoominbutton = QtGui.QPushButton('Zoom In')
	self.zoomoutbutton = QtGui.QPushButton('Zoom Out')
	buttonsize = [int(self.screenres[1]/4 ), int(self.screenres[1]/2)]
	self.highresbutton = QtGui.QPushButton('1024x768')
	self.lowresbutton = QtGui.QPushButton('640x480')
	self.highresbutton.setCheckable(True)
	self.lowresbutton.setCheckable(True)
	self.lowresbutton.setChecked(True)
	self.highresbutton.setFixedSize(buttonsize[0],buttonsize[1])
	self.lowresbutton.setFixedSize(buttonsize[0],buttonsize[1])
	self.zoominbutton.setFixedSize(buttonsize[0],buttonsize[1])
	self.zoomoutbutton.setFixedSize(buttonsize[0],buttonsize[1])
        self.zoominbutton.toggled.connect(self.zoomin) 
	self.setupPlots()
        self.canvasrow = FigureCanvas(self.figurerow)
	self.canvascolumn = FigureCanvas(self.figurecolumn)

	self.expslider.valueChanged[int].connect(self.changeExposure)
        self.zoominbutton.clicked.connect(self.zoomin) 
        self.zoomoutbutton.clicked.connect(self.zoomout) 
	self.lowresbutton.clicked.connect(self.lowres)
	self.highresbutton.clicked.connect(self.highres)

	layout.addWidget(self.videowindow,   0,0,2,1)
	layout.addWidget(self.canvasrow,     2,0,2,1)
	layout.addWidget(self.canvascolumn,  0,1,2,1)
	layout.addWidget(self.expslider,     0,5,2,1)
	layout.addWidget(self.expbar,        0,4,2,1)
#	layout.addWidget(self.lowresbutton,  0,2)
#	layout.addWidget(self.highresbutton, 1,2)
#	layout.addWidget(self.zoominbutton,  0,3)
#	layout.addWidget(self.zoomoutbutton, 1,3)
	layout.addWidget(self.xwaist,        2,1)
	layout.addWidget(self.ywaist,        3,1)

        self.setLayout(layout)

    def startCamera(self):
	# capture frames from the camera
	for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):

		# grab the raw NumPy array representing the image
		image = frame.array

		#take the green part of the image
		greenimage = image[:,:,1]
		globmax = np.max(greenimage)

		#cv2 thingy
 		key = cv2.waitKey(1) & 0xFF

		#create array for plotting with the number of pixels in each axis
		xpixels = np.linspace(0,len(greenimage[0,:]),len(greenimage[0,:]))
		ypixels = np.linspace(0,len(greenimage[:,0]),len(greenimage[:,0]))

		#row and colum sum for live plots
		columnsum = greenimage.sum(axis=1)/40.0
		rowsum = greenimage.sum(axis=0)/40.0

		#subtract minumum value (background subtraction)
		columnsum = columnsum - np.min(columnsum)
		rowsum = rowsum - np.min(rowsum)

		#Init Guess for fitting
		columnampguess = columnsum.max()
		columncenterguess = np.argmax(columnsum[::-1])

		rowampguess = rowsum.max()
		rowcenterguess = np.argmax(rowsum)
		percexp = 100 * globmax/255.0
		self.expbar.setValue(percexp)

		#Curve fit rowsum and column sum to gaussian, fit parameters returned in popt1/2
		try:
			popt1, pcov1 = curve_fit(self.func, xpixels, rowsum, p0=[rowampguess,rowcenterguess,200])
			popt2, pcov2 = curve_fit(self.func, ypixels, columnsum[::-1], p0=[columnampguess,columncenterguess,200])

		except:
			popt1, popt2 = [[0,0,1], [0,0,1]]

		#updates data for row and column plots, also mirrors column data
        	self.linesrow.set_xdata(xpixels)
        	self.linesrow.set_ydata(rowsum)

        	self.linescolumn.set_xdata(columnsum[::-1])
        	self.linescolumn.set_ydata(ypixels)

		#updates data for fit row and column plots
        	self.linesrowfit.set_xdata(xpixels)
        	self.linesrowfit.set_ydata(self.func(xpixels, popt1[0],popt1[1],popt1[2]))

        	self.linescolumnfit.set_xdata(self.func(ypixels, popt2[0],popt2[1],popt2[2]))
        	self.linescolumnfit.set_ydata(ypixels)


        	#draw data and flush
        	self.figurerow.canvas.draw()
        	self.figurerow.canvas.flush_events()

        	self.figurecolumn.canvas.draw()
        	self.figurecolumn.canvas.flush_events()

        	#update X and Y waist labels with scaled waists
		self.xwaist.setText('X = ' + str(np.abs(popt1[2]*2*5.875))[0:5] + 'um')
		self.ywaist.setText('Y = ' +str(np.abs(popt2[2]*2*5.875))[0:5]  + 'um')

		# convert RGB image np array to qPixmap and update canvas widget
		qPixmap = self.nparrayToQPixmap(image)
		videoy = int(self.screenres[0]/2.1)
		videox = int(1.333 * videoy)
		self.videowindow.setPixmap(qPixmap.scaled(videox,videoy))
 
		# clear the stream in preparation for the next frame
		self.rawCapture.truncate(0)

    def setupPlots(self):

        #Set up plot axes and figure positions
        self.figurerow, self.axrow = plt.subplots()
	#self.figurerow.gca().set_position([0,0,1,1])

        self.figurecolumn, self.axcolumn = plt.subplots()
	#self.figurecolumn.gca().set_position([0,0,1,1])

	#Create line objects for fast plot redrawing
        self.linesrow, = self.axrow.plot([],[],linewidth=2,color='purple')
        self.linesrowfit, = self.axrow.plot([],[],linestyle='--',linewidth=2,color='yellow')

        self.linescolumn, = self.axcolumn.plot([],[],linewidth=2,color='purple')
	self.linescolumnfit, = self.axcolumn.plot([],[],linestyle='--',linewidth=2,color='yellow')

        self.axrow.set_xlim(0, self.imageres[0])
	self.axrow.set_ylim(0,300)

        self.axcolumn.set_xlim(0, 300)
	self.axcolumn.set_ylim(0,self.imageres[1])

	self.axrow.xaxis.set_ticks_position('none')
	self.axrow.yaxis.set_ticks_position('none')
	self.axrow.get_xaxis().set_visible(False)
	self.axrow.get_yaxis().set_visible(False)
	self.axrow.patch.set_visible(False)

	self.axcolumn.xaxis.set_ticks_position('none')
	self.axcolumn.yaxis.set_ticks_position('none')
	self.axcolumn.get_xaxis().set_visible(False)
	self.axcolumn.get_yaxis().set_visible(False)
	self.axcolumn.patch.set_visible(False)

    def changeExposure(self, value):
	scaledvalue = 0.5 * value**2 + 1
	self.camera.shutter_speed = int(scaledvalue)

    #gaussian function used in fitting routine
    def func(self, x, a, x0, sigma):
   	return a*np.exp(-(x-x0)**2/(2*sigma**2))

    #converts nparray to qpixmap
    def nparrayToQPixmap(self, arrayImage):
    	pilImage = toimage(arrayImage)
    	qtImage = ImageQt(pilImage)
    	qImage = QtGui.QImage(qtImage)
    	qPixmap = QtGui.QPixmap(qImage)
    	return qPixmap

    #to be added
    def zoomin(self):
	if self.zoom >= 10:
		self.zoom = 10
	else:
		self.zoom += 1
		self.resizePlots()

    def zoomout(self):
	if self.zoom <= 1:
		self.zoom = 1
	else:
		self.zoom -= 1
		self.resizePlots()

    def lowres(self):
	self.highresbutton.setChecked(False)

    def highres(self):
	self.lowresbutton.setChecked(False)

    def resizePlots(self):
	gaprow = self.imageres[0]*(self.zoom * 0.04)
        self.axrow.set_xlim(gaprow, self.imageres[0] - gaprow)
	self.axrow.set_ylim(0,300)

	gapcolumn = self.imageres[1]*(self.zoom * 0.04)
        self.axcolumn.set_xlim(0, 300)
	self.axcolumn.set_ylim(gapcolumn,self.imageres[1] - gapcolumn)

if __name__ == "__main__":

    a = QtGui.QApplication([])
    proflayoutwidget = proflayout()
    proflayoutwidget.show()
    proflayoutwidget.startCamera()
    sys.exit(a.exec_())


