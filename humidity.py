import Adafruit_DHT
import time
import datetime
import sqlite3

DHT_SENSOR = Adafruit_DHT.AM2302
DHT_PIN = 4

con = sqlite3.connect('weedwatcher.db')
cur = con.cursor()

while True:
	humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
	
	if humidity is not None and temperature is not None:
		print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
		print("Timestamp: " + str(datetime.datetime.now()))
		cur.execute("INSERT INTO humidity VALUES(?, ?)", (humidity, str(datetime.datetime.now())))
		cur.execute("INSERT INTO temperature VALUES(?, ?)", (temperature, str(datetime.datetime.now())))
		con.commit()
	else:
		print("Failed to retrieve data from humidity sensor")

	time.sleep(5)
