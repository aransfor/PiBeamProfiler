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
from PyQt4 import QtGui
import numpy as np
from scipy.misc.pilutil import toimage
from scipy.optimize import curve_fit
import time, sys
import cv2

class profiler(QtGui.QWidget):
    
    def __init__(self):
        super(profiler, self).__init__()
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
	#set main geometry and title
        self.setGeometry(400, 150, 650, 550)
        self.setWindowTitle('Beam Profiler')
        layout = QtGui.QGridLayout()

        #Set up plot axes and figure positions
        self.figurerow, self.axrow = plt.subplots()
	self.figurerow.gca().set_position([0,0,1,1])

        self.figurecolumn, self.axcolumn = plt.subplots()
	self.figurecolumn.gca().set_position([0,0,1,1])

	#Create line objects for fast plot redrawing
        self.linesrow, = self.axrow.plot([],[],linewidth=2,color='purple')
        self.linesrowfit, = self.axrow.plot([],[],linestyle='--',linewidth=2,color='yellow')

        self.linescolumn, = self.axcolumn.plot([],[],linewidth=2,color='purple')
	self.linescolumnfit, = self.axcolumn.plot([],[],linestyle='--',linewidth=2,color='yellow')
	
	#axis attributes (mostly stripping borders and tick marks)
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

	#set plot limits and aspect ratios
        self.axrow.set_xlim(0, 640)
	self.axrow.set_ylim(0,100)
	self.axrow.set_aspect(0.33333)

        self.axcolumn.set_xlim(0, 100)
	self.axcolumn.set_ylim(0,480)
	self.axcolumn.set_aspect(3)


        #Create canvas, label and button widgets
        self.canvasrow = FigureCanvas(self.figurerow)
	self.canvascolumn = FigureCanvas(self.figurecolumn)

	self.videowindow = QtGui.QLabel()

	self.xwaist = QtGui.QLabel()
	self.ywaist = QtGui.QLabel()

	self.zoominbutton = QtGui.QPushButton('+')
	self.zoomoutbutton = QtGui.QPushButton('-')
	
	#fixes sizes for display widgets
	self.videowindow.resize(640,480)

	self.canvasrow.setMinimumHeight(50)
	self.canvasrow.setMaximumHeight(50)

	self.canvascolumn.setMinimumWidth(50)
	self.canvascolumn.setMaximumWidth(50)

	#add widgets to layout grid
        layout.addWidget(self.canvasrow,4,0,3,5)
        layout.addWidget(self.canvascolumn,0,5,5,3)

        layout.addWidget(self.videowindow  ,0,0,5,5)

        layout.addWidget(self.zoominbutton  ,4,11,1,1)
	layout.addWidget(self.zoomoutbutton  ,4,9,1,1)

        layout.addWidget(self.xwaist  ,3,9,1,1)
        layout.addWidget(self.ywaist  ,3,10,1,1)

	#connect buttons to functions
        self.zoominbutton.toggled.connect(self.zoomin) 

	#set layout
        self.setLayout(layout)
	
    def startCamera(self):
	# capture frames from the camera
	for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):

		# grab the raw NumPy array representing the image
		image = frame.array

		#take the green part of the image
		greenimage = image[:,:,1]

		#cv2 thingy
 		key = cv2.waitKey(1) & 0xFF

		#create array for plotting with the number of pixels in each axis
		xpixels = np.linspace(0,len(greenimage[0,:]),len(greenimage[0,:]))
		ypixels = np.linspace(0,len(greenimage[:,0]),len(greenimage[:,0]))

		#row and colum sum for live plots
		columnsum = greenimage.sum(axis=1)
		rowsum = greenimage.sum(axis=0)

		#subtract minumum value (background subtraction)
		columnsum = columnsum - np.min(columnsum)
		rowsum = rowsum - np.min(rowsum)

		#Curve fit rowsum and column sum to gaussian, fit parameters returned in popt1/2
		popt1, pcov1 = curve_fit(self.func, xpixels, rowsum, p0=[80,300,50])
		popt2, pcov2 = curve_fit(self.func, ypixels, columnsum[::-1], p0=[80,240,50])

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
		self.xwaist.setText('X waist = ' + str(np.abs(popt1[2]*2*5.875))[0:5] + 'um')
		self.ywaist.setText('Y waist = ' +str(np.abs(popt2[2]*2*5.875))[0:5]  + 'um')

		# convert RGB image np array to qPixmap and update canvas widget
		qPixmap = self.nparrayToQPixmap(image)
		self.videowindow.setPixmap(qPixmap)	
 
		# clear the stream in preparation for the next frame
		self.rawCapture.truncate(0)
		if not self.running:
			break

    #to be added
    def zoomin(self):
	pass

    #converts nparray to qpixmap
    def nparrayToQPixmap(self, arrayImage):
    	pilImage = toimage(arrayImage)
    	qtImage = ImageQt(pilImage)
    	qImage = QtGui.QImage(qtImage)
    	qPixmap = QtGui.QPixmap(qImage)
    	return qPixmap

    #gaussian function used in fitting routine
    def func(self, x, a, x0, sigma):
   	return a*np.exp(-(x-x0)**2/(2*sigma**2))


if __name__ == "__main__":

    a = QtGui.QApplication([])
    profilerwidget = profiler()
    profilerwidget.show()
    profilerwidget.startCamera()
    sys.exit(a.exec_())
