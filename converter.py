
# Image conversion handling

import pygame
import log4p
from PIL import Image

import config as CONFIG


class Converter:

	log = None

	# Constructor
	def __init__(self):

		logger = log4p.GetLogger(__name__, config=CONFIG.LOG4P_CONFIG)
		self.log = logger.logger
		self.log.info("Initializing Converter...")


	def startup(self):

		self.log.info("Starting Converter...")


	def shutdown(self):

		self.log.info("Shutting down Converter...")
		pygame.quit()


	# Maximize color value, round it to int.
	def get_max(self, value):
		if value > 255:
			return 255
		return int(value)


	# Convert image to grayscale.
	def toGrayscale(self, picture, effectRatio):

		self.log.debug("Converting to grayscale...")

		width, height = picture.get_size()
		pilString = pygame.image.tostring(picture.convert(), "RGB", False)
		pilImage = Image.frombytes("RGB", picture.get_size(), pilString)

		# Grayscale:
		# 0.299 R, 0.587 G, 0.114 B

		r = 0.299 * effectRatio
		g = 0.587 * effectRatio
		b = 0.114 * effectRatio
		rn = 1 - (1-0.299) * effectRatio
		gn = 1 - (1-0.587) * effectRatio
		bn = 1 - (1-0.114) * effectRatio
		#self.log.debug("r: " + str(r) + " g: " + str(g) + " b: " + str(b))
		#self.log.debug("rn: " + str(rn) + " gn: " + str(gn) + " bn: " + str(bn))

		grayscale = (
			rn, g, b, 0,
			r, gn, b, 0,
			r, g, bn, 0)

		output = pilImage.convert("RGB", grayscale)

		self.log.debug("Conversion done.")

		return pygame.image.fromstring(output.tobytes(), output.size, output.mode).convert()


	# Convert one color to grayscale
	def toGrayscaleColor(self, color, effectRatio):

		# r = 1 - (1-0.299) * effectRatio
		# g = 1 - (1-0.587) * effectRatio
		# b = 1 - (1-0.114) * effectRatio

		y = 0.299 * color[0] + 0.589 * color[1] + 0.114 * color[2]
		r = (1-effectRatio) * color[0] + effectRatio * y
		g = (1-effectRatio) * color[1] + effectRatio * y
		b = (1-effectRatio) * color[2] + effectRatio * y

		#return (self.get_max(color[0]*r), self.get_max(color[1]*g), self.get_max(color[2]*b))
		return (self.get_max(r), self.get_max(g), self.get_max(b))


	# Convert to sepia.
	def toSepia(self, picture, effectRatio):

		self.log.debug("Converting to sepia...")

		width, height = picture.get_size()
		pilString = pygame.image.tostring(picture.convert(), "RGB", False)
	
		# First convert to grayscale
		pilImage = Image.frombytes("RGB", picture.get_size(), pilString).convert("L").convert("RGB")

		# Now apply a matrix conversion
		r = 1 - (1-1.3) * effectRatio
		g = 1 - (1-0.9) * effectRatio
		b = 1 - (1-0.5) * effectRatio
		#self.log.debug("r: " + str(r) + " g: " + str(g) + " b: " + str(b))

		sepia = (
			r, 0, 0, 0,
			0, g, 0, 0,
			0, 0, b, 0)

		output = pilImage.convert("RGB", sepia)

		self.log.debug("Conversion done.")
	
		return pygame.image.fromstring(output.tobytes(), output.size, output.mode).convert()


	# Convert one color to sepia
	def toSepiaColor(self, color, effectRatio):

		r = 1 - (1-1.3) * effectRatio
		g = 1 - (1-0.9) * effectRatio
		b = 1 - (1-0.5) * effectRatio

		return (self.get_max(color[0]*r), self.get_max(color[1]*g), self.get_max(color[2]*b))
	