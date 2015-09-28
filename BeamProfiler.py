# import the necessary packages
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
from picamera.array import PiRGBArray
from picamera import PiCamera
from PyQt4 import QtGui
import matplotlib.pyplot as plt
import numpy as np
from scipy.misc.pilutil import toimage
from scipy.optimize import curve_fit
from PIL.ImageQt import ImageQt
import time, sys
import cv2

class profiler(QtGui.QWidget):
    
    def __init__(self):
        super(profiler, self).__init__()
	# initialize the camera and grab a reference to the raw camera capture
	self.camera = PiCamera()
	self.maxresolution = [640, 480]
	self.camera.resolution = (640, 480)
	self.camera.framerate = 33
	self.camera.shutter_speed = 500
	self.camera.exposure_mode = 'off'
	self.camera.iso = 300
	self.rawCapture = PiRGBArray(self.camera, size=(640, 480))
	self.running = True
	self.zoom = 0.1
	# allow the camera to warmup
	time.sleep(0.1)
	self.initializeGUI()

    def initializeGUI(self):
        self.setGeometry(400, 150, 650, 550)
        self.setWindowTitle('Beam Profiler')
        layout = QtGui.QGridLayout()
	self.videowindow = QtGui.QLabel()
        self.figurerow = plt.figure(frameon=False)
	self.figurecolumn = plt.figure(frameon=False)

        #Set up plot
        self.figurerow, self.axrow = plt.subplots()
        self.figurecolumn, self.axcolumn = plt.subplots()

	self.figurerow.gca().set_position([0,0,1,1])
	self.figurecolumn.gca().set_position([0,0,1,1])

        self.linesrow, = self.axrow.plot([],[],linewidth=2,color='purple')
        self.linesrowfit, = self.axrow.plot([],[],linestyle='--',linewidth=2,color='yellow')
        self.linescolumn, = self.axcolumn.plot([],[],linewidth=2,color='purple')
	self.linescolumnfit, = self.axcolumn.plot([],[],linestyle='--',linewidth=2,color='yellow')	

	self.axcolumn.xaxis.set_ticks_position('none')
	self.axrow.xaxis.set_ticks_position('none')

	self.axcolumn.yaxis.set_ticks_position('none')

	self.axrow.yaxis.set_ticks_position('none')

	self.axcolumn.get_xaxis().set_visible(False)
	self.axcolumn.get_yaxis().set_visible(False)
	self.axrow.get_xaxis().set_visible(False)
	self.axrow.get_yaxis().set_visible(False)

        self.axrow.set_xlim(0, 640)
	self.axrow.set_ylim(0,100)
	self.axrow.set_aspect(0.33333)
	self.axrow.patch.set_visible(False)

        self.axcolumn.set_xlim(0, 100)
	self.axcolumn.set_ylim(0,480)
	self.axcolumn.set_aspect(3)
	self.axcolumn.patch.set_visible(False)

        #Other stuff
        #self.axrow.grid([1,5])
	#self.axcolumn.grid([5,1])
        self.canvasrow = FigureCanvas(self.figurerow)
	self.canvascolumn = FigureCanvas(self.figurecolumn)
	self.xwaist = QtGui.QLabel()
	self.ywaist = QtGui.QLabel()
	self.zoominbutton = QtGui.QPushButton('+')
	self.zoomoutbutton = QtGui.QPushButton('-')

	self.panupbutton = QtGui.QPushButton('up')
	self.pandownbutton = QtGui.QPushButton('down')
	self.panrightbutton = QtGui.QPushButton('right')
	self.panleftbutton = QtGui.QPushButton('left')

	self.videowindow.resize(640,480)
	self.canvasrow.setMinimumHeight(50)
	self.canvascolumn.setMinimumWidth(50)
	self.canvasrow.setMaximumHeight(50)
	self.canvascolumn.setMaximumWidth(50)

        layout.addWidget(self.canvasrow,4,0,3,5)
        layout.addWidget(self.canvascolumn,0,5,5,3)

        layout.addWidget(self.videowindow  ,0,0,5,5)
        layout.addWidget(self.zoominbutton  ,4,11,1,1)
        layout.addWidget(self.xwaist  ,3,9,1,1)
        layout.addWidget(self.ywaist  ,3,10,1,1)

	layout.addWidget(self.zoomoutbutton  ,4,9,1,1)

        layout.addWidget(self.panupbutton  ,0,10,1,1)
        layout.addWidget(self.pandownbutton  ,2,10,1,1)
        layout.addWidget(self.panrightbutton  ,1,11,1,1)
        layout.addWidget(self.panleftbutton  ,1,9,1,1)

        self.zoominbutton.toggled.connect(self.zoomin) 


        self.setLayout(layout)
	
    def startCamera(self):
	# capture frames from the camera
	for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
		# grab the raw NumPy array representing the image, then initialize the timestamp
		# and occupied/unoccupied text
		image = frame.array
		greenimage = image[:,:,1]
 		key = cv2.waitKey(1) & 0xFF
		xpixels = np.linspace(0,len(greenimage[0,:]),len(greenimage[0,:]))
		ypixels = np.linspace(0,len(greenimage[:,0]),len(greenimage[:,0]))
		data = greenimage
		columnsum = data.sum(axis=1)
		rowsum = data.sum(axis=0)
		columnsum = columnsum - np.min(columnsum)
		rowsum = rowsum - np.min(rowsum)
		columnsum = columnsum*85/columnsum.max()
		rowsum = rowsum*85/rowsum.max()

		popt1, pcov1 = curve_fit(self.func, xpixels, rowsum, p0=[80,300,50])
		popt2, pcov2 = curve_fit(self.func, ypixels, columnsum[::-1], p0=[80,240,50])

        	self.linesrow.set_xdata(xpixels)
        	self.linesrow.set_ydata(rowsum)

        	self.linesrowfit.set_xdata(xpixels)
        	self.linesrowfit.set_ydata(self.func(xpixels, popt1[0],popt1[1],popt1[2]))
		self.xwaist.setText('X waist = ' + str(np.abs(popt1[2]*2*5.875))[0:5] + 'um')
		self.ywaist.setText('Y waist = ' +str(np.abs(popt2[2]*2*5.875))[0:5]  + 'um')
        	#self.linesrow.set_ydata(self.func(xpixels, popt[0],popt[1],popt[2]))
        	self.figurerow.canvas.draw()
        	self.figurerow.canvas.flush_events()
        	#self.canvasrow.draw()

        	self.linescolumn.set_xdata(columnsum[::-1])
        	self.linescolumn.set_ydata(ypixels)

        	self.linescolumnfit.set_xdata(self.func(ypixels, popt2[0],popt2[1],popt2[2]))
        	self.linescolumnfit.set_ydata(ypixels)

        	self.figurecolumn.canvas.draw()
        	self.figurecolumn.canvas.flush_events()
        	#self.canvascolumn.draw()

		# show the frame
		qPixmap = self.nparrayToQPixmap(image)
		self.videowindow.setPixmap(qPixmap)	
 
		# clear the stream in preparation for the next frame
		self.rawCapture.truncate(0)
		if not self.running:
			break

    def zoomin(self):
	if self.zoom >= 1.0:
		self.zoom = 1.0
	elif self.zoom <= 0.1:
		self.zoom = 0.1
	else:
		self.zoom -= 0.1
	
		

    def stopClicked(self):
	self.running = False

    def nparrayToQPixmap(self, arrayImage):
    	pilImage = toimage(arrayImage)
    	qtImage = ImageQt(pilImage)
    	qImage = QtGui.QImage(qtImage)
    	qPixmap = QtGui.QPixmap(qImage)
    	return qPixmap

    def func(self, x, a, x0, sigma):
   	return a*np.exp(-(x-x0)**2/(2*sigma**2))


if __name__ == "__main__":

    a = QtGui.QApplication([])
    profilerwidget = profiler()
    profilerwidget.show()
    profilerwidget.startCamera()
    sys.exit(a.exec_())
