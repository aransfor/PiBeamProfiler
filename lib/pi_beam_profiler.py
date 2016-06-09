import picamera as _picamera
import picamera.array as _array
import time as _time
import numpy as _n
import camera_image as _ci


class PiBeamProfiler(object):
    """
    beam profiler object for raspberry-pi.

    To use the beam profiler:

    self.initialize_camera()
    self.run_beam_profiler()

    """

    def __init__(self):
        """
        Attributes
        ----------
        resolution_mode: str, resolution mode of the camera.
            Options: "high", "low". default('low')
        """
        self.resolution_mode = 'low'
        self.camera_format = 'bgr'
        self.color = 'red'
        self.coarsen = False

    def restart_camera(self):
        self.close_camera()
        self.initialize_camera()
        self.run_beam_profiler()

    def initialize_camera(self):
        # initialize the camera
        self.camera = _picamera.PiCamera()
        # set camera resolution, gain , sutter speed and framerate
        self._set_camera_resolution()
        self.camera.framerate = 33  # in Hz
        self.set_camera_shutter_speed(100)  # in us
        self.camera.exposure_mode = 'off'
        self.camera.iso = 300
        # grab a reference to the raw camera capture
        rgbarray = _array.PiRGBArray
        self.current_frame = rgbarray(self.camera, size=self.camera_resolution)
        # allow the camera to warmup
        _time.sleep(0.1)

    def set_camera_resolution_mode(self, mode='low'):
        if mode in ('low', 'high'):
            self.resolution_mode = mode
        else:
            self.resolution_mode = 'low'

    def prepare_for_raw_image(self, raw_image):
        # raw image taken from camera is upside down
        inverted_array = self._convert_raw_image_to_numpy_array(raw_image)
        # flip the inverted array
        array = inverted_array[::-1]
        image = self._set_image_color(array)
        camera_image = _ci.CameraImage(image=image, coarsen=self.coarsen)
        return camera_image

    def _set_camera_resolution(self):
        if self.resolution_mode == 'high':
            self.camera_resolution = (1296, 972)
        else:
            self.camera_resolution = (640, 480)
        self.camera.resolution = self.camera_resolution

    def set_camera_shutter_speed(self, shutter_speed):
        """ Set shutter speed in us. """
        self.camera.shutter_speed = shutter_speed

    def _convert_raw_image_to_numpy_array(self, raw_image):
        array = _n.nan_to_num(raw_image.array)
        return array

    def _set_image_color(self, array):
        """ Pick color pixel to use for image. Default(red). """
        red_image = array[:, :, 0]
        green_image = array[:, :, 1]
        blue_image = array[:, :, 2]
        if self.color == 'green':
            image = green_image
        elif self.color == 'blue':
            image = blue_image
        else:
            image = red_image
        return image

    def set_image_color(self, color):
        if color in ['red', 'green', 'blue']:
            self.color = color

    def close_camera(self):
        self.camera.close()
