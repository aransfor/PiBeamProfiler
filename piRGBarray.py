import picamera
import picamera.array

with picamera.PiCamera() as camera:
	with picamera.array.PiRGBArray(camera) as output:
		camera.capture(output, 'rgb')
		print('Captured %dx%d image' % (
			output.array.shape[1], output.array.shape[0]))
