from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from PyQt4 import QtGui, QtCore
from PIL.ImageQt import ImageQt
import numpy as np
from scipy.misc.pilutil import toimage
import sys

class proflayout(QtGui.QWidget):

    def __init__(self):
        super(proflayout, self).__init__()
	self.zoom = 1
	self.imageres = [640,480]
	desktop = QtGui.QDesktopWidget()
	screensize = desktop.screenGeometry()
	self.screenres = [800,480]
#	self.screenres = [screensize.width(),screensize.height()]
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
	buttonsize = [int(self.screenres[1]/4 ), int(self.screenres[1]/2 - 50)]
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
        self.canvasrow = FigureCanvas(self.figurerow)
	self.canvascolumn = FigureCanvas(self.figurecolumn)
	self.makePlots()

        self.zoominbutton.clicked.connect(self.zoomin) 
        self.zoomoutbutton.clicked.connect(self.zoomout) 
	self.lowresbutton.clicked.connect(self.lowres)
	self.highresbutton.clicked.connect(self.highres)

	layout.addWidget(self.videowindow,   0,0,2,1)
	layout.addWidget(self.canvasrow,     2,0,2,1)
	layout.addWidget(self.canvascolumn,  0,1,2,1)
	layout.addWidget(self.expslider,     0,5,2,1)
	layout.addWidget(self.expbar,        0,4,2,1)
	layout.addWidget(self.lowresbutton,  0,2)
	layout.addWidget(self.highresbutton, 1,2)
	layout.addWidget(self.zoominbutton,  0,3)
	layout.addWidget(self.zoomoutbutton, 1,3)
	layout.addWidget(self.xwaist,        2,1)
	layout.addWidget(self.ywaist,        3,1)

        self.setLayout(layout)

    def setupPlots(self):

	self.figurerow, self.axrow = plt.subplots()
	self.figurerow.gca().set_position([0,0,1,1])

        self.figurecolumn, self.axcolumn = plt.subplots()
	self.figurecolumn.gca().set_position([0,0,1,1])

        self.linesrow, = self.axrow.plot([],[],linewidth=2,color='purple')
        self.linescolumn, = self.axcolumn.plot([],[],linewidth=2,color='red')

        self.axrow.set_xlim(0, self.imageres[0])
	self.axrow.set_ylim(0,150)

        self.axcolumn.set_xlim(0, 150)
	self.axcolumn.set_ylim(0,self.imageres[1])

    def makePlots(self):

	xrow = np.linspace(0,self.imageres[0],self.imageres[0])
        self.linesrow.set_xdata(xrow)
        self.linesrow.set_ydata(150 - 100*np.exp(-(xrow - 320)**2/100))

	ycolumn = np.linspace(0,self.imageres[1],self.imageres[1])
        self.linescolumn.set_xdata(100*np.exp(-(ycolumn - 240)**2/100))
        self.linescolumn.set_ydata(ycolumn)

        #draw data and flush
        self.figurerow.canvas.draw()
        self.figurerow.canvas.flush_events()

        self.figurecolumn.canvas.draw()
        self.figurecolumn.canvas.flush_events()

        #update X and Y waist labels with scaled waists
	self.xwaist.setText('X Waist = ' + '126.5' + 'um')
	self.ywaist.setText('Y Waist = ' + '128.4'  + 'um')
	x = np.linspace(0,640,640)
	y = np.linspace(0,480,480)
	xx, yy = np.meshgrid(x,y)
	z = np.exp(-0.01*((xx - 320)**2 + (yy - 240)**2))
	qPixmap = self.nparrayToQPixmap(z)
	videoy = int(self.screenres[0]/2.1)
	videox = int(1.333 * videoy)
	self.videowindow.setPixmap(qPixmap.scaled(videox,videoy))	

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
	self.axrow.set_ylim(0,150)

	gapcolumn = self.imageres[1]*(self.zoom * 0.04)
        self.axcolumn.set_xlim(0, 150)
	self.axcolumn.set_ylim(gapcolumn,self.imageres[1] - gapcolumn)
	self.makePlots()


if __name__ == "__main__":

    a = QtGui.QApplication([])
    proflayoutwidget = proflayout()
    proflayoutwidget.show()
    sys.exit(a.exec_())


