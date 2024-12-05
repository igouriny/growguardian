# # Imports
# import sys
# import paho.mqtt.client as paho
# import time
# import RPi.GPIO as GPIO
# import adafruit_dht
# import board
# from datetime import datetime
#
# # MQTT setup
# BROKER = "localhost"  # Replace with your broker's address
# PORT = 1883
# TOPIC = "iot/sensor_data"  # Topic to publish sensor data
#
# # Initialize DHT11 sensor
# dht_device = adafruit_dht.DHT11(board.D4) # Temp / Humidity Sensor
#
# # Setup Pins
# led_pin = 5
# moisture_sensor_pin = 6
# relay_pin = 17
#
# # Setup GPIO
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(led_pin, GPIO.OUT) # Light
# GPIO.setup(moisture_sensor_pin, GPIO.IN) # Moisture Sensor
# GPIO.setup(relay_pin, GPIO.OUT) # Relay Switch
#
# # Function to Turn light On or Off based on time.
# def control_light():
# 	now = datetime.now()
# 	# Light will be on between 9:00AM to 6:30PM or else is OFF
# 	if (now.hour >= 9 and now.hour <18) or (now.hour == 18 and now.minute < 30):
# 		GPIO.output(led_pin, GPIO.HIGH) # Lights On
# 	else:
# 		GPIO.output(led_pin, GPIO.LOW) # Light Off
#
# def read_soil_moisture():
#     # Read digital value: 1 = Dry, 0 = Wet
#     moisture_status = GPIO.input(moisture_sensor_pin)
#     if moisture_status == 0:
#         return "Wet"
#     else:
#         return "Dry"
#
# # Function to turn the pump ON.
# def pump_on():
#     GPIO.output(relay_pin, GPIO.HIGH)
#     print("Pump is ON")
#
# # Function to turn the pump OFF.
# def pump_off():
#     GPIO.output(relay_pin, GPIO.LOW)
#     print("Pump is OFF")
#
# # Function to water the plant if soil is Dr
# def water_plant():
# 	soil_status = read_soil_moisture()
# 	print(f"Soil Moisture: {soil_status}")
# 	if soil_status == "Wet":
# 		pump_on()
# 		time.sleep(0.2) # Pump will be on for 0.5 seconds
# 		pump_off()
# 		time.sleep(10) # Will not let it be run again for 10 seconds
# 	else:
# 		time.sleep(2)
#
# # Check if can conncet to client
# client = paho.Client()
#
# if client.connect(BROKER, PORT, 60) != 0:
#     print("Couldn't connect to the MQTT broker")
#     sys.exit(1)
#
# def send_temp_and_humid():
# 	# Read temperature and humidity
# 	temperature = dht_device.temperature
# 	humidity = dht_device.humidity
#
# 	if temperature is not None and humidity is not None:
# 		# Prepare payload and publish to MQTT topic
# 		payload = [temperature, humidity]
# 		# Publishs payload to MQTT Topic
# 		client.publish(TOPIC, str(payload))
# 		print(f"Published: {payload} to topic {TOPIC}")
# 	else:
# 		print("Failed to retrieve data from sensor.")
# 		# Wait 2 seconds before next publish
# 		time.sleep(2)
#
# # Main
# try:
#     while True:
#         try:
#             control_light()
#             water_plant()
#             send_temp_and_humid()
#
#         except RuntimeError as error:
#             print(f"RuntimeError: {error}")
#             time.sleep(2)
# except KeyboardInterrupt:
#     print("Exiting program.")
# finally:
#     dht_device.exit()
#     GPIO.cleanup()
#     client.disconnect()
