
# Configuration

# Platform dependent stuff
FULLSCREEN = True
BASE_FOLDER = "/home/pi/tv/"
ADC_ENABLED = False
FORECAST_ENABLED = False
BME280_ENABLED = False

#RENDER_MODE = "Manual"
RENDER_MODE = "Timed"
RANDOMIZE = True

RENDER_SLEEP = 30

# Potmeters
ADC_SLEEP = 0.5
MAX_ADC_VALUE = 2600

# BME 280
BME280_PORT = 1
BME280_ADDRESS = 0x76

# Display settings
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480

BACKGROUND_COLOR = (0, 0, 0)

IMAGE_CENTER_RATIO = 0.70

MINIMUM_TIME_WIDTH = 0.15
MAXIMUM_TIME_WIDTH = 0.25

TIME_MARGIN_TOP = 0.01
TIME_MARGIN_RIGHT = 0.05
TIME_MARGIN_BOTTOM = 0.01
TIME_MARGIN_LEFT = 0.05

TIME_FONT = ("Retro60Prime.ttf", "porter-sans-inline-block.ttf", "retro.ttf")
TIME_FALLBACK_FONT = "Lekton-Regular.ttf"
TIME_COLOR = ((170, 170, 255), (170, 170, 255), (200, 200, 200))
TIME_FONT_HEIGHT_COMP = (1.1, 1.1, 1.1)
TIME_TEMP_CHAR = ("", u"\u00b0", "")
TIME_HUM_CHAR = ("", "%", "%")

OPENWEATHERMAP_ID = xxx
FORECAST_COUNT = 4
FORECAST_STEP = 4
FORECAST_HEIGHT = 200
FORECAST_FILES = ("Thunderstorm", "Drizzle", "Rain", "Snow", "Fog", "Clear", "Clouds")
FORECAST_FILE_EXT = ".png"


# Logging
LOG4P_CONFIG = BASE_FOLDER + "log4p.json"

# Fonts
FONT_FOLDER = BASE_FOLDER + "fonts/"

# Media to display
MEDIA_FOLDER = BASE_FOLDER + "media/"

# Additional images
IMAGE_FOLDER = BASE_FOLDER + "images/"
IMAGE_MODE_FOLDER = ("normal", "retro", "sepia")




