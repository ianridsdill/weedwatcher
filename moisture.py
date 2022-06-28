import RPi.GPIO as GPIO
import time

MOISTURE_POWER_GPIO = 26
MOISTURE_SENSOR_GPIO = 21

DELAY = 10 #seconds

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_POWER_GPIO, GPIO.OUT)
GPIO.setup(MOISTURE_SENSOR_GPIO, GPIO.IN)

MOISTURE_OK = 0

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

		# sleep
		time.sleep(DELAY)

except KeyboardInterrupt:
	GPIO.cleanup()

# incorporate motion sensor to take more frequent readings if motion detected (ie, someone watering the plants)
