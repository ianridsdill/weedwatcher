import RPi.GPIO as GPIO
import time
import datetime
import sqlite3
import flask
import codecs
import multiprocessing

# define GPIO pins here
MOISTURE_POWER_GPIO = 26
MOISTURE_SENSOR_GPIO = 21

# how often will readings be taken?
DELAY = 10 #seconds

# set GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_POWER_GPIO, GPIO.OUT)
GPIO.setup(MOISTURE_SENSOR_GPIO, GPIO.IN)
GPIO.setwarnings(False)

# variables
MOISTURE_OK = 0

# set up SQLite connection
connection = sqlite3.connect('weedwatcher.db')
cursor = connection.cursor()

# set up Flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# define API endpoints
@app.route('/', methods=['GET'])
def home():
	return codecs.open("index.html", 'r').read()

app.run(host='0.0.0.0')

# start sensor readings
try:
	while True:
		# turn on sensor
		GPIO.output(MOISTURE_POWER_GPIO, 1)
		time.sleep(1)

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

except KeyboardInterrupt:
	GPIO.cleanup()

# incorporate motion sensor to take more frequent readings if motion detected (ie, someone watering the plants)
# add email or sms notification when plant needs watering
# add cooldown so that user is not notified for successive dry readings
