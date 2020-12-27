
# Display handling

import pygame
import pygame.freetype
import log4p
import os
import traceback
import datetime
import random

import config as CONFIG
import converter

class Display:

	log = None
	screen = None
	media = []
	clock = None
	converter = converter.Converter()

	imageFolder = 0
	imageMode = 0			# normal, grayscale, sepia
	imageLeft = True
	effectRatio = 0
	timeMode = 0
	imageIndex = 0
	lastResizeResult = [None, 1, None]
	lastTimeResult = False

	normalFont = None
	retroFont = None
	renderChannel = True


	# Constructor
	def __init__(self, clock):

		logger = log4p.GetLogger(__name__, config=CONFIG.LOG4P_CONFIG)
		self.log = logger.logger
		self.log.info("Initializing Display...")

		self.clock = clock

		# Init pygame, get the screen surface
		os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
		pygame.init()
		info = pygame.display.Info()
		self.log.info(info)
		
		if (CONFIG.FULLSCREEN):
			self.screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
			pygame.mouse.set_visible(False)
			#BUGBUG: only on windows... pygame.display.set_allow_screensaver(False)
			#FIX KA 20201110: resolution differs when starting from console or xwindows...
			CONFIG.DISPLAY_WIDTH = info.current_w
			CONFIG.DISPLAY_HEIGHT = info.current_h
		else:
			self.screen = pygame.display.set_mode((CONFIG.DISPLAY_WIDTH, CONFIG.DISPLAY_HEIGHT), pygame.RESIZABLE)

		self.enumerateImages()


	def startup(self):

		self.log.info("Starting Display...")


	def shutdown(self):

		self.log.info("Shutting down Display...")
		pygame.quit()

	
	def enumerateImages(self):

		if (self.imageFolder == 0):
			path = CONFIG.MEDIA_FOLDER
		else:
			path = CONFIG.MEDIA_FOLDER + str(self.imageFolder)

		self.log.debug("Enumerating images in " + path)
		self.media = []
		for (dirpath, dirnames, filenames) in os.walk(path):
			for filename in filenames:
				self.media.append(os.path.join(dirpath, filename))
				#self.log.debug(dirpath + filename + " - " + str(len(self.media)))
		
		self.log.debug("Found " + str(len(self.media)) + " files.")
		self.imageIndex = 0
		self.renderChannel = True

		if (CONFIG.RANDOMIZE):
			random.shuffle(self.media)


	def render(self, selectNextImage, selectNextClock = True):

		self.log.debug("Rendering...")

		# Select next image, next time mode (only if time was rendered)
		if (selectNextImage):
			self.imageIndex = self.imageIndex + 1
			if (self.imageIndex >= len(self.media)):
				self.imageIndex = 0

			if (self.lastResizeResult[1] == 2):
				self.imageLeft = not self.imageLeft

			if (self.lastTimeResult and selectNextClock):
				self.timeMode = self.timeMode + 1
				if (self.timeMode == 5):
					self.timeMode = 0

		# Clear screen
		fullRect = pygame.Rect(0, 0, CONFIG.DISPLAY_WIDTH, CONFIG.DISPLAY_HEIGHT)
		self.screen.fill(CONFIG.BACKGROUND_COLOR, fullRect)

		self.lastResizeResult = self.renderImage()
		self.lastTimeResult = self.renderTime(self.lastResizeResult)

		# Force centering if time is not displayed
		if (self.lastTimeResult == False):
			self.screen.fill(CONFIG.BACKGROUND_COLOR, fullRect)
			self.lastResizeResult = self.renderImage(True)

		if (self.renderChannel):
		    self.write(str(self.imageFolder + 1), 50, CONFIG.TIME_FONT[self.imageMode], 10, 10, self.screen)
		    self.renderChannel = False

		# Update screen
		pygame.display.update(fullRect)



	# Render the next image.
	def renderImage(self, toCenter = False):

		self.log.debug("Rendering image...")

		if (len(self.media) == 0):
			font = pygame.font.Font(pygame.font.get_default_font(), 20)
			text = font.render("No images.", True, (0, 128, 0))	
			self.screen.blit(text, (0, 0))		
			return (None, 2, pygame.Rect(0, 0, CONFIG.DISPLAY_WIDTH/2, CONFIG.DISPLAY_HEIGHT))

		try:

			self.log.debug("Loading " + self.media[self.imageIndex])
			surface = pygame.image.load(self.media[self.imageIndex])
			resizeResult = self.resize(surface, toCenter)
			
			if (self.imageMode == 0):
				img = resizeResult[0]

			if (self.imageMode == 1):
				img = self.converter.toGrayscale(resizeResult[0], self.effectRatio)		

			if (self.imageMode == 2):
				img = self.converter.toSepia(resizeResult[0], self.effectRatio)		
	
			self.screen.blit(img, resizeResult[2])

		except Exception as e:
			self.log.error("Unexpected error: " + str(e))
			print(traceback.format_exc())
		
		return resizeResult


	# Resize the image to fit to the screen.
	def resize(self, picture, toCenter = False):
	
		originalRect = picture.get_rect()
		self.log.debug("Original image size: " + str(originalRect[2]) + "x" + str(originalRect[3]))

		if (originalRect[2] == 0 or originalRect[3] == 0):
			return (picture, 0, originalRect)

		scaleWidth = float(CONFIG.DISPLAY_WIDTH)/float(originalRect[2])
		scaleHeight = float(CONFIG.DISPLAY_HEIGHT)/float(originalRect[3])

		if (scaleHeight > scaleWidth):
			imgScale = scaleWidth
			scaleMode = 1
		else:
			imgScale = scaleHeight
			scaleMode = 2

		newRect = pygame.Rect(0, 0, originalRect[2] * imgScale, originalRect[3] * imgScale)		

		# Center vertically, or center horizontally - but leave space for the time.
		if (scaleHeight > scaleWidth):
			newRect[1] = (CONFIG.DISPLAY_HEIGHT - newRect[3]) / 2
		else:		
			if (newRect[2] < CONFIG.DISPLAY_WIDTH * CONFIG.IMAGE_CENTER_RATIO):
				if (self.imageLeft):
					newRect[0] = (CONFIG.DISPLAY_WIDTH * CONFIG.IMAGE_CENTER_RATIO - newRect[2]) / 2
				else:
					newRect[0] = CONFIG.DISPLAY_WIDTH - newRect[2] - (CONFIG.DISPLAY_WIDTH * CONFIG.IMAGE_CENTER_RATIO - newRect[2]) / 2
			if (toCenter):
				newRect[0] = (CONFIG.DISPLAY_WIDTH - newRect[2]) / 2

		self.log.debug("New image size: " + str(newRect[2]) + "x" + str(newRect[3]) + ", left: " + str(newRect[0]))
		picture = pygame.transform.scale(picture, (newRect[2], newRect[3]))
		return [picture, scaleMode, newRect]


	# Resize for width only
	def resizeForWidth(self, picture, width):
	
		originalRect = picture.get_rect()
		self.log.debug("Original image size: " + str(originalRect[2]) + "x" + str(originalRect[3]))

		if (originalRect[2] == 0 or originalRect[3] == 0):
			return (picture, 0, originalRect)

		imgScale = float(width)/float(originalRect[2])

		newRect = pygame.Rect(0, 0, originalRect[2] * imgScale, originalRect[3] * imgScale)		

		self.log.debug("New image size: " + str(newRect[2]) + "x" + str(newRect[3]))
		picture = pygame.transform.scale(picture, (newRect[2], newRect[3]))
		return [picture, newRect]


	# Render the date, time, temperature etc.
	def renderTime(self, resizeResult):

		self.log.debug("Rendering time and temp...")

		if (resizeResult[1] == 1):
			self.log.debug("Skipping time, image is landscape oriented.")
			return False

		today = datetime.datetime.now()
		
		if (self.imageLeft):
			availWidth = CONFIG.DISPLAY_WIDTH - resizeResult[2][0] - resizeResult[2][2] 
		else:
			availWidth = resizeResult[2][0]

		width =  availWidth - (availWidth * CONFIG.TIME_MARGIN_LEFT * 2)
		self.log.debug("Available width: " + str(availWidth) + ", minimum: " + str(CONFIG.DISPLAY_WIDTH * CONFIG.MINIMUM_TIME_WIDTH) + ", maximum: " + str(CONFIG.DISPLAY_WIDTH * CONFIG.MAXIMUM_TIME_WIDTH))

		# If width is too small, don't render
		if (width < CONFIG.DISPLAY_WIDTH * CONFIG.MINIMUM_TIME_WIDTH):
			self.log.debug("Skipping time, image is too wide.")
			return False

		# If width is too large, text will overflow at the bottom
		if (width > CONFIG.DISPLAY_WIDTH * CONFIG.MAXIMUM_TIME_WIDTH):
			width = CONFIG.DISPLAY_WIDTH * CONFIG.MAXIMUM_TIME_WIDTH
			self.log.debug("Reached maximum width.")

		# Align left or right
		if (self.imageLeft):
			left = resizeResult[2][0] + resizeResult[2][2] + (availWidth - width) / 2
		else:
			left = (availWidth - width) /2
		
		# Verical alignment will be computed later
		top = 0
		self.log.debug("Width: " + str(width) + ", left: " + str(left) + ", top: " + str(top) + ", image to left: " + str(self.imageLeft))

		# Render this to a temp surface, so we can position it vertically at the end.
		destSurface = pygame.Surface((int(width)+5, CONFIG.DISPLAY_HEIGHT))


		if (self.timeMode == 0):
			# Render date
			top = top + self.write(today.strftime("%Y"), width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
			top = top + self.write(today.strftime("%m"), width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
			top = top + self.write(today.strftime("%d"), width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
			top = top + self.write(today.strftime("%A"), width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]

		if (self.timeMode == 1):
			# Render time
			top = top + self.write(today.strftime("%H"), width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
			top = top + self.write(today.strftime("%M"), width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]

		if (self.timeMode == 2):
			# Render inside temp
			if (CONFIG.TIME_TEMP_CHAR[self.imageMode] == ""):
				result = self.write(u"\u00b0", width/4, CONFIG.TIME_FALLBACK_FONT, width * 3/4, top, destSurface)
				top = top + self.write("{:.0f}".format(self.clock.insideTemp), width-result[0], CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
				result = self.write("%", width/4, CONFIG.TIME_FALLBACK_FONT, width * 3/4, top, destSurface)
				top = top + self.write("{:.0f}".format(self.clock.insideHum), width-result[0], CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
			else:
				top = top + self.write("{:.0f}".format(self.clock.insideTemp) + CONFIG.TIME_TEMP_CHAR[self.imageMode], width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
				top = top + self.write("{:.0f}".format(self.clock.insideHum) + CONFIG.TIME_HUM_CHAR[self.imageMode], width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
			
			top = top + self.write("{:.0f}".format(self.clock.pressure) + " hPa", width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]

		if (self.timeMode == 3):
			# Render outside temp
			if (CONFIG.TIME_TEMP_CHAR[self.imageMode] == ""):
				result = self.write(u"\u00b0", width/4, CONFIG.TIME_FALLBACK_FONT, width * 3/4, top, destSurface)
				top = top + self.write("{:.0f}".format(self.clock.outsideTemp), width-result[0], CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
				result = self.write("%", width/4, CONFIG.TIME_FALLBACK_FONT, width * 3/4, top, destSurface)
				top = top + self.write("{:.0f}".format(self.clock.outsideHum), width-result[0], CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
			else:
				top = top + self.write("{:.0f}".format(self.clock.outsideTemp) + CONFIG.TIME_TEMP_CHAR[self.imageMode], width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]
				top = top + self.write("{:.0f}".format(self.clock.outsideHum) + CONFIG.TIME_HUM_CHAR[self.imageMode], width, CONFIG.TIME_FONT[self.imageMode], 0, top, destSurface)[1]

			# First forecast is the actual one
			surface = pygame.image.load(CONFIG.IMAGE_FOLDER + CONFIG.IMAGE_MODE_FOLDER[self.imageMode] + "/" 
				+ CONFIG.FORECAST_FILES[self.clock.forecast[0]] + CONFIG.FORECAST_FILE_EXT)
				
			# Resize icon and do a color conversion too
			resizeResult = self.resizeForWidth(surface, width)

			if (self.imageMode == 1):
				resizeResult[0] = self.converter.toGrayscale(resizeResult[0], self.effectRatio)		

			if (self.imageMode == 2):
				resizeResult[0] = self.converter.toSepia(resizeResult[0], self.effectRatio)		

			resizeResult[1][1] = top
			destSurface.blit(resizeResult[0], resizeResult[1])
			top = top + resizeResult[1][3]


		if (self.timeMode == 4):
			# Render forecast
			for i in range(1, len(self.clock.forecast)):
				surface = pygame.image.load(CONFIG.IMAGE_FOLDER + CONFIG.IMAGE_MODE_FOLDER[self.imageMode] + "/" 
					+ CONFIG.FORECAST_FILES[self.clock.forecast[i]] + CONFIG.FORECAST_FILE_EXT)
				
				# Resize icon and do a color conversion too
				resizeResult = self.resizeForWidth(surface, width)

				if (self.imageMode == 1):
					resizeResult[0] = self.converter.toGrayscale(resizeResult[0], self.effectRatio)		

				if (self.imageMode == 2):
					resizeResult[0] = self.converter.toSepia(resizeResult[0], self.effectRatio)		

				resizeResult[1][1] = top
				destSurface.blit(resizeResult[0], resizeResult[1])
				top = top + resizeResult[1][3] + CONFIG.DISPLAY_HEIGHT * CONFIG.TIME_MARGIN_TOP

		# Render to screen
		top = (CONFIG.DISPLAY_HEIGHT - top) / 2
		if (top < CONFIG.DISPLAY_HEIGHT * CONFIG.TIME_MARGIN_TOP):
			top = CONFIG.DISPLAY_HEIGHT * CONFIG.TIME_MARGIN_TOP
	
		self.screen.blit(destSurface, (left, top))
		return True


	# Render text to the available width
	def write(self, text, widthToFit, fontName, x, y, destSurface):

		fontSize = 1
		size = (0, 0, 0, 0)
		fontExists = os.path.exists(CONFIG.FONT_FOLDER + fontName)

		if (fontExists):
			font = pygame.freetype.Font(CONFIG.FONT_FOLDER + fontName, fontSize)
		else:
			self.log.error("No such font: " + CONFIG.FONT_FOLDER + fontName + ", using: " + pygame.font.get_default_font())
			font = pygame.freetype.SysFont(pygame.font.get_default_font(), fontSize)

		# Faster mode: use size parameter in get_rect.
		while (size[2] < widthToFit):		
			fontSize = fontSize + 1
			size = font.get_rect(text, size=fontSize)

		# Change color too
		color = CONFIG.TIME_COLOR[self.imageMode]

		if (self.imageMode == 1):
			color = self.converter.toGrayscaleColor(color, self.effectRatio)

		if (self.imageMode == 2):
			color = self.converter.toSepiaColor(color, self.effectRatio)

		result = font.render_to(destSurface, (x, y), text, color, size=fontSize) 

		return (result[2], result[3] * CONFIG.TIME_FONT_HEIGHT_COMP[self.imageMode])


	# Set mode according to the ADC value.
	def changeMode(self, adcValue, doRender):

		# Select mode
		if (adcValue[0] <= 10):
			self.imageMode = 0
			self.effectRatio = 0

		if (adcValue[0] > 10 and adcValue[0] < CONFIG.MAX_ADC_VALUE / 2):
			self.imageMode = 1
			self.effectRatio = adcValue[0] / CONFIG.MAX_ADC_VALUE * 2

		if (adcValue[0] > CONFIG.MAX_ADC_VALUE / 2):
			self.imageMode = 2
			self.effectRatio = (adcValue[0] - CONFIG.MAX_ADC_VALUE / 2) / CONFIG.MAX_ADC_VALUE * 2
			if (self.effectRatio > 1):
				self.effectRatio = 1

		self.log.debug("Mode set to: " + str(self.imageMode) + ", effect ratio: " + str(self.effectRatio))

		newFolder = int(adcValue[1]/260)
		if (newFolder > 10):
			newFolder = 10
		
		if (newFolder != self.imageFolder):
			self.imageFolder = newFolder
			self.enumerateImages()


		if (doRender):
			self.render(False)
