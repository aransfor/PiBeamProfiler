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

        self.linesrow, = self.axrow.plot([],[])
        self.linescolumn, = self.axcolumn.plot([],[])
	
	self.axcolumn.xaxis.set_ticks_position('none')
	self.axrow.xaxis.set_ticks_position('none')
	self.axcolumn.yaxis.set_ticks_position('none')
	self.axrow.yaxis.set_ticks_position('none')

	self.axcolumn.get_xaxis().set_visible(False)
	self.axcolumn.get_yaxis().set_visible(False)
	self.axrow.get_xaxis().set_visible(False)
	self.axrow.get_yaxis().set_visible(False)

        self.axrow.set_xlim(0, 480)
	self.axrow.set_ylim(0,100)
	self.axrow.set_aspect(0.142857)
	self.axrow.patch.set_visible(False)

        self.axcolumn.set_xlim(0, 100)
	self.axcolumn.set_ylim(0,480)
	self.axcolumn.set_aspect(7)
	self.axcolumn.patch.set_visible(False)

        #Other stuff
        #self.axrow.grid([1,5])
	#self.axcolumn.grid([5,1])
        self.canvasrow = FigureCanvas(self.figurerow)
	self.canvascolumn = FigureCanvas(self.figurecolumn)
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

        	self.linesrow.set_xdata(xpixels)
        	self.linesrow.set_ydata(rowsum/480)
        	self.figurerow.canvas.draw()
        	self.figurerow.canvas.flush_events()
        	#self.canvasrow.draw()

        	self.linescolumn.set_xdata(columnsum/480)
        	self.linescolumn.set_ydata(ypixels)
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


if __name__ == "__main__":

    a = QtGui.QApplication([])
    profilerwidget = profiler()
    profilerwidget.show()
    profilerwidget.startCamera()
    sys.exit(a.exec_())
