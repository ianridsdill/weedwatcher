import RPi.GPIO as GPIO
import multiprocessing

# define GPIO pins here
MOISTURE_POWER_GPIO = 26

MOISTURE_SENSOR_1_GPIO = 21
MOISTURE_SENSOR_1_LABEL = 'Strain #1'

MOISTURE_SENSOR_2_GPIO = 19
MOISTURE_SENSOR_2_LABEL = 'Strain #2'

# set GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_POWER_GPIO, GPIO.OUT)
GPIO.setup(MOISTURE_SENSOR_1_GPIO, GPIO.IN)
GPIO.setup(MOISTURE_SENSOR_2_GPIO, GPIO_IN)
GPIO.setwarnings(False)

# set up Flask api
def flask():
	import flask
	import codecs

	app = flask.Flask(__name__)
	app.config["DEBUG"] = False

	# define API endpoints

	# default
	@app.route('/', methods=['GET'])
	def home():
		return codecs.open("index.html", 'r').read()

	@app.route('/derp', methods=['GET'])
	def derp():
		return '''<h2>herp derp test test</h2>'''

	app.run(host='0.0.0.0')

# start sensor readings
def moisture_sensor_start():
	import RPi.GPIO as GPIO
	import time
	import datetime
	import sqlite3

	connection = sqlite3.connect('weedwatcher.db')
	cursor = connection.cursor()

	DELAY = 10 #seconds
	MOISTURE_1_OK = 0
	MOISTURE_2_OK = 0

	try:
		while True:
			# turn on sensors
			GPIO.output(MOISTURE_POWER_GPIO, 1)
			time.sleep(1) # give the sensor time to turn on before taking a reading

			# sensor 1 - determine wet or not wet
			if GPIO.input(MOISTURE_SENSOR_1_GPIO):
				print(MOISTURE_SENSOR_1_LABEL + " is dry, go water it!")
				MOISTURE_1_OK = 0
			else:
				print(MOISTURE_SENSOR_1_LABEL + " is fine. Relax.")
				MOISTURE_1_OK = 1

			# sensor 2 - determine wet or not wet
			if GPIO.input(MOISTURE_SENSOR_2_GPIO):
				print(MOISTURE_SENSOR_2_LABEL + " is dry, go water it!")
				MOISTURE_2_OK = 0
			else:
				print(MOISTURE_SENSOR_2_LABEL + " is fine. Relax.")
				MOISTURE_2_OK = 1

			# turn off sensor
			GPIO.output(MOISTURE_POWER_GPIO, 0)

			# write result to db
			cursor.execute("INSERT INTO moisture VALUES(?, ?, ?, ?)", (MOISTURE_1_OK, str(datetime.datetime.now(), 1, MOISTURE_SENSOR_1_LABEL)))
			cursor.execute("INSERT INTO moisture VALUES(?, ?, ?, ?)", (MOISTURE_2_OK, str(datetime.datetime.now(), 2, MOISTURE_SENSOR_2_LABEL)))
			connection.commit()

			# sleep
			time.sleep(DELAY)

	except KeyboardInterrupt: # stop sensor readings and reset GPIO pins
		GPIO.cleanup()

# start each part of the app in it's own process

# start flask api
process_flask = multiprocessing.Process(target=flask, args=())

process_flask.start()

# start reading from moisture_sensor
process_moisture_sensor = multiprocessing.Process(target=moisture_sensor_start, args=())

process_moisture_sensor.start()

# start reading from temp+humidity sensor

# incorporate motion sensor to take more frequent readings if motion detected (ie, someone watering the plants)
# add email or sms notification when plant needs watering
# add cooldown so that user is not notified for successive dry readings
