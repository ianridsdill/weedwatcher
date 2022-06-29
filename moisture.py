import RPi.GPIO as GPIO
import multiprocessing

# define GPIO pins here
MOISTURE_POWER_GPIO = 26
MOISTURE_SENSOR_GPIO = 21

# set GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_POWER_GPIO, GPIO.OUT)
GPIO.setup(MOISTURE_SENSOR_GPIO, GPIO.IN)
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
	MOISTURE_OK = 0

	try:
		while True:
			# turn on sensor
			GPIO.output(MOISTURE_POWER_GPIO, 1)
			time.sleep(1) # give the sensor time to turn on before taking a reading

			# determine wet or not wet
			if GPIO.input(MOISTURE_SENSOR_GPIO):
				print("Plant is dry, go water it!")
				MOISTURE_OK = 0
			else:
				print("Plant is fine. Relax.")
				MOISTURE_OK = 1

			# turn off sensor
			GPIO.output(MOISTURE_POWER_GPIO, 0)

			# write result to db
			cursor.execute("INSERT INTO moisture VALUES(?, ?)", (MOISTURE_OK, str(datetime.datetime.now())))
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
