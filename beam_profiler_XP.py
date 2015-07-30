#test
import picamera as p
from PIL import Image
import numpy as np
import time

class BeamProfiler(object):
    def __init__(self):
        pass

    def take_image(self, a_res, b_res, shutter, filename='beam_image.jpg'):
        with p.PiCamera() as c:
            c.resolution = (a_res, b_res)
	    c.shutter_speed = shutter
	    """
	    Will add user preview toggling before capture
	    """
	    c.start_preview()
	    time.sleep(5)
	    c.stop_preview()
            c.capture(filename)
        image = Image.open(filename)
        image = image.convert('LA')
        array = np.array(list(image.getdata()))
        self.array = array[:, 0].reshape(a_res, b_res)
        self.image = Image.fromarray(self.array) 
