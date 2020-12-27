
# Soviet TV displaying photos, time and temperature
# Based on the Timedisc code.
# (C): Adam Katona, 2020

import time
import traceback
import log4p
import pygame
import locale
import keyboard

import config as CONFIG
import display
import clock
import Adafruit_ADS1x15


# Stop all stuff.
def doHalt():

	log.info("Shutting down app...")
	clock.shutdown()
	display.shutdown()
	quit()


# Init stuff
logger = log4p.GetLogger(__name__, config=CONFIG.LOG4P_CONFIG)
log = logger.logger

locale.setlocale(locale.LC_ALL, 'hu_HU.utf8')

clock = clock.Clock()
display = display.Display(clock)

clock.startup()
display.startup()

sleepCycleCount = int(CONFIG.RENDER_SLEEP/CONFIG.ADC_SLEEP)

if (CONFIG.ADC_ENABLED):
	adc = Adafruit_ADS1x15.ADS1115()
	adcValue = [round(adc.read_adc(0, gain=1) / 100) * 10, round(adc.read_adc(1, gain=1) / 100) * 10]
	display.changeMode(adcValue, False)

if (CONFIG.RENDER_MODE == "Manual"):
	log.debug("Manual mode, press i or c.")
	display.render(True)


# Main loop.
while True:

	try:

		# Update clock
		clock.update()

		# Show display
		if (CONFIG.RENDER_MODE == "Timed"):
			display.render(True)

		# Idle wait, checking the ADC
		for i in range(0, sleepCycleCount):

			time.sleep(CONFIG.ADC_SLEEP)

			# Check potmeters
			if (CONFIG.ADC_ENABLED):
				newValue = [round(adc.read_adc(0, gain=1) / 100) * 10, round(adc.read_adc(1, gain=1) / 100) * 10]

				if (newValue[0] != adcValue[0] or newValue[1] != adcValue[1]):
					log.debug("ADC value change: " + str(newValue[0]) + ", " + str(newValue[1]))
					adcValue = newValue
					display.changeMode(adcValue, True)

				if (newValue[1] != adcValue[1]):
					i = 0

			# Check keyboard in manual mode
			if (CONFIG.RENDER_MODE == "Manual"):
				if (keyboard.is_pressed('i')): 
					log.debug("I pressed, selecting next image.")
					display.render(True, False)

				if (keyboard.is_pressed('c') or keyboard.is_pressed(' ')): 
					log.debug("C pressed, selecting next clock and image.")
					display.render(True, True)

				if (keyboard.is_pressed('e')):
					log.debug("E pressed, changing effect.")
					display.imageMode = display.imageMode + 1
					if (display.imageMode > 2):
						display.imageMode = 0
					display.render(False)			

				if (keyboard.is_pressed('r')):
					log.debug("R pressed, increasing effect ratio.")
					display.effectRatio = display.effectRatio + 0.1
					if (display.effectRatio > 1):
						display.effectRatio = 0
					display.render(False)	

			pygame.event.pump()


	except (KeyboardInterrupt):

		doHalt()

	except Exception as e:

		log.error("Unexpected error: " + str(e))
		print(traceback.format_exc())

		
