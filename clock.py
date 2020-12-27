
# Clock and temperature handling

import pygame
import log4p
import os
import requests
import smbus2
import bme280

import config as CONFIG


class Clock:

	log = None
	screen = None
	bus = None
	calibration_params = None

	insideTemp = 20.0
	outsideTemp = 12.0
	insideHum = 75.0
	outsideHum = 82.0
	pressure = 1000

	forecast = [5, 5, 5]

	cycle = 0


	# Constructor
	def __init__(self):

		logger = log4p.GetLogger(__name__, config=CONFIG.LOG4P_CONFIG)
		self.log = logger.logger
		self.log.info("Initializing Clock...")

		if (CONFIG.BME280_ENABLED):
			self.bus = smbus2.SMBus(CONFIG.BME280_PORT)
			self.calibration_params = bme280.load_calibration_params(self.bus, CONFIG.BME280_ADDRESS)


	def startup(self):

		self.log.info("Starting Clock...")


	def shutdown(self):

		self.log.info("Shutting down Clock...")
		pygame.quit()


	def update(self):

		# Get inside temperature
		if (CONFIG.BME280_ENABLED):
			self.log.debug("Getting temperature...")
			data = bme280.sample(self.bus, CONFIG.BME280_ADDRESS, self.calibration_params)
			self.insideTemp = data.temperature
			self.insideHum = data.humidity
			self.pressure = data.pressure

		# Get outside temperature and forecast
		self.cycle = self.cycle + 1
		if (CONFIG.FORECAST_ENABLED and (self.cycle == 1 or self.cycle * CONFIG.RENDER_SLEEP > 60*60*2)):
			self.cycle = 1
			self.log.debug("Getting forecast...")
			url = "https://api.openweathermap.org/data/2.5/forecast?q=R%C3%A1koscsaba,%20HU&appid=" + CONFIG.OPENWEATHERMAP_ID
			response = requests.get(url, timeout=(2,5))

			if (response):
				forecast = response.json()

				# Current outside
				self.outsideTemp = forecast["list"][0]["main"]["temp"] - 273.15
				self.outsideHum = forecast["list"][0]["main"]["humidity"]

				# Forecast
				self.forecast = []
				for i in range(0, CONFIG.FORECAST_COUNT):
					weather = forecast["list"][CONFIG.FORECAST_STEP * i]["weather"][0]["main"]
					self.log.debug("Forecast for " + str(i) + ": " + weather)

					try:
						self.forecast.append(CONFIG.FORECAST_FILES.index(weather))
					except ValueError:
						self.forecast.append(-1)


			else:
				self.log.error("Can't get forecast.")
