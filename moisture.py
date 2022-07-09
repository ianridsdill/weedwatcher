import RPi.GPIO as GPIO
import multiprocessing
import Adafruit_DHT
import sqlite3
import datetime
import time

# define GPIO pins here
MOISTURE_POWER_GPIO = 26

MOISTURE_SENSOR_1_GPIO = 21
MOISTURE_SENSOR_1_LABEL = 'Strain #1'

MOISTURE_SENSOR_2_GPIO = 19
MOISTURE_SENSOR_2_LABEL = 'Strain #2'

MOISTURE_SENSOR_3_GPIO = 13
MOISTURE_SENSOR_3_LABEL = 'Strain #3'

DHT_SENSOR_GPIO = 4
DHT_SENSOR_TYPE = Adafruit_DHT.AM2302

# set GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_POWER_GPIO, GPIO.OUT)
GPIO.setup(MOISTURE_SENSOR_1_GPIO, GPIO.IN)
GPIO.setup(MOISTURE_SENSOR_2_GPIO, GPIO.IN)
GPIO.setup(MOISTURE_SENSOR_3_GPIO, GPIO.IN)
GPIO.setwarnings(False)

# set up sqlite stuff
connection = sqlite3.connect('weedwatcher.db')
cursor = connection.cursor()

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
	MOISTURE_DELAY = 10 # in seconds. delay between readings

	MOISTURE_1_OK = 0
	MOISTURE_2_OK = 0
	MOISTURE_3_OK = 0

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

			# sensor 3 - determine wet or not wet
			if GPIO.input(MOISTURE_SENSOR_3_GPIO):
				print(MOISTURE_SENSOR_3_LABEL + " is dry, go water it!")
				MOISTURE_3_OK = 0
			else:
				print(MOISTURE_SENSOR_3_LABEL + " is fine. Relax.")
				MOISTURE_3_OK = 1

			# turn off sensor
			GPIO.output(MOISTURE_POWER_GPIO, 0)

			# write result to db
			cursor.execute("INSERT INTO moisture VALUES(?, ?, ?, ?)", (MOISTURE_1_OK, str(datetime.datetime.now()), 1, MOISTURE_SENSOR_1_LABEL))
			cursor.execute("INSERT INTO moisture VALUES(?, ?, ?, ?)", (MOISTURE_2_OK, str(datetime.datetime.now()), 2, MOISTURE_SENSOR_2_LABEL))
			cursor.execute("INSERT INTO moisture VALUES(?, ?, ?, ?)", (MOISTURE_3_OK, str(datetime.datetime.now()), 3, MOISTURE_SENSOR_3_LABEL))
			connection.commit()

			# sleep
			time.sleep(MOISTURE_DELAY)

	except KeyboardInterrupt: # stop sensor readings and reset GPIO pins
		GPIO.cleanup()

def humidity_temperature_sensor_start():
	TEMP_HUMIDITY_DELAY = 5 # seconds

	try:
		while True:
			humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, DHT_SENSOR_GPIO)
	
			if humidity is not None and temperature is not None:
				print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
				print("Timestamp: " + str(datetime.datetime.now()))

				cursor.execute("INSERT INTO humidity VALUES(?, ?)", (humidity, str(datetime.datetime.now())))
				cursor.execute("INSERT INTO temperature VALUES(?, ?)", (temperature, str(datetime.datetime.now())))
				connection.commit()

			else:
				print("Failed to retrieve data from humidity sensor")

			time.sleep(TEMP_HUMIDITY_DELAY)

	except KeyboardInterrupt:
		GPIO.cleanup()


# start each part of the app in it's own process

# start flask api
process_flask = multiprocessing.Process(target=flask, args=())

process_flask.start()

# start reading from moisture_sensor
process_moisture_sensor = multiprocessing.Process(target=moisture_sensor_start, args=())

process_moisture_sensor.start()

process_temperature_humidity = multiprocessing.Process(target=humidity_temperature_sensor_start, args=())

process_temperature_humidity.start()

# start reading from temp+humidity sensor

# incorporate motion sensor to take more frequent readings if motion detected (ie, someone watering the plants)
# add email or sms notification when plant needs watering
# add cooldown so that user is not notified for successive dry readings
