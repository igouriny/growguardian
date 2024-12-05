# Define the MQTT settings
import paho.mqtt.client as mqtt

BROKER = "192.168.143.12"  # Use "localhost" or the IP of the Raspberry Pi for remote access
PORT = 1883  # Change port to 1883 for MQTT
TOPIC = "iot/sensor_data"


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC)


sensor_data = {"temperature": [], "humidity": []}


def on_message(client, userdata, msg):
    data = msg.payload.decode().split(',')
    temperature, humidity = data[0], data[1]
    sensor_data["temperature"].append(temperature)
    sensor_data["humidity"].append(humidity)
    print(temperature, humidity)

    # Write the data to a file
    with open("historicaldata.txt", "a") as file:
        file.write(f"{temperature},{humidity}\n")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(BROKER, PORT, keepalive=60)  # Ensure keepalive is set as an integer

# Start the loop to process network traffic
client.loop_start()
