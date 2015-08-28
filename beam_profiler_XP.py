import picamera as p
from PIL import Image
import numpy as np
import time

class BeamProfiler(object):
	"""Beam Profiler class"""
	def __init__(self):
		self.a_res = 100
		self.b_res = 100
		self.shutter_default = 250
		self.shutter = 250
		self.iso = 100
	
	def take_image(self, filename='beam_image.jpg'):
		"""Takes an image and prepares image data 
		for fitting"""
		with p.PiCamera() as c:
			c.resolution = (self.a_res, self.b_res)
			c.shutter_speed = self.shutter
			c.iso = self.iso
			c.capture(filename)
		image = Image.open(filename)
		self.image_raw = image
		image = image.convert('LA')
		self.array_raw = np.array(list(image.getdata()))
		self.array = self.array_raw[:, 0].reshape(self.a_res, self.b_res)
		self.image = Image.fromarray(self.array)

	def take_image_preview(self, filename='beam_image.jpg'):
		"""Starts with a preview, then takes an image and 
		prepares image data for fitting"""
		with p.PiCamera() as c:
			c.shutter_speed = self.shutter
			c.resolution = (self.a_res, self.b_res)
			c.start_preview()
			raw_input("Press enter to capture...")
			c.stop_preview()
			c.capture(filename)
		image = Image.open(filename)
		self.image_raw = image
		image = image.convert('LA')
		array = np.array(list(image.getdata()))
		self.array = array[:, 0].reshape(self.a_res, self.b_res)
		self.image = Image.fromarray(self.array) 

	def see_preview(self):
		"""Starts a preview"""
		with p.PiCamera() as c:
			c.resolution = (self.a_res, self.b_res)
			c.start_preview()
			raw_input("Press enter to continue...")
			c.stop_preview()

#	"""
#	The work in progress on an algorithm that optimizes the shutter speed 
#	based on minimizing the number of pixels that are maxed out
#	"""
#	def calibrate_shutter_simple(self):
#		self.shutter = self.shutter_default
#		im0 = self.take_image()
#		max_pix0 = np.amax(self.array_raw)
#		cal = False
#		if max_pix0 == 255:
#			while cal is False:
#				self.shutter = self.shutter - 10
#				print 'decreasing shutter speed --> ', self.shutter
#				im1 = self.take_image()
#				max_pix1 = np.amax(self.array_raw)
#				print 'max pixel value = ', max_pix1
#				if max_pix1 < 255 and max_pix1 >= 0:
#					cal = True
#				elif max_pix1 > 255:
#					print 'ERROR'
#					break
#		elif max_pix0 < 240 and max_pix0 >= 0:
#			while cal is False:
#				self.shutter = self.shutter + 1
#				print 'increasig shutter speed --> ', self.shutter
#				im1 = self.take_image()
#				max_pix1 = np.amax(self.array_raw)
#				print 'max pixel value = ', max_pix1
#				if max_pix1 < 240 and max_pix1 >= 0:
#					cal = True
#				elif max_pix1 > 255:
#					print 'ERROR'
#					break
#		else:
#			print 'ERROR'
#		return self.shutter
#
#	def calibrate_shutter
#		with p.PiCamera() as c:
#			c.resolution = (self.a_res, self.b_res)
#			c.shutter_speed = self.shutter_default
#			im0 = self.take_image()
#			max_pix0 = np.amax(im0.array)
#			cal = False
#			acc = False
#			count = 0
#			while max_pix0 = 255
#				while cal is False
#					c.shuter_speed = c.shutter_speed - 10
#					im1 = self.take_image()
#					max_pix1 = np.amax(im1.array)
#					if max_pix1 <= 254 and max_pix1 >= 0
#						count = count + 1
#						while acc is False 
#							im2 = self.take_image()
#							max_pix2 = np.amax(im2.array)
#							if max_pix2 <= 254 and max_pix2 >= 0
#								count = count + 1
#							if count == 5
#								
#			while max_pix0 <= 254 and max_pix0 >= 0
#				default = 'Low'
#			else
#				print 'ERROR'
