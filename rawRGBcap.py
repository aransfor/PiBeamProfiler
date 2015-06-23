import time
import picamera
iport picamera.array

with picamera.PiCamera() as camera:
	with picamera.array.PiRGBArray(camera) as stream:
		camera.resolution = (1024, 768)
		camera.start_preview()
		time.sleep(2)
		camera.capture(stream, 'rgb')
		print(stream.array.shape)
