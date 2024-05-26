import paho.mqtt.client as mqtt
import json
import time

MQTT_SERVER = "mqttserver.tk"
MQTT_PORT = 1883
MQTT_USERNAME = "innovation"
MQTT_PASSWORD = "Innovation_RgPQAZoA5N"
MQTT_TOPIC_PUB = "/innovation/pumpcontroller/station"
MQTT_TOPIC_SUB = "/innovation/pumpcontroller/station"

def mqtt_connected(client, userdata, flags, rc):
    print("Connected successfully!!")
    client.subscribe(MQTT_TOPIC_SUB)

def mqtt_subscribed(client, userdata, mid, granted_qos):
    print("Subscribed to Topic!!!")

def mqtt_recv_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    try:
        data = json.loads(payload)
        print("Received JSON:", data)
        # You can process the JSON data here
    except json.JSONDecodeError as e:
        # print(f"Received non-JSON message: {payload}")
        print("Error decoding JSON message: ", e)


mqttClient = mqtt.Client()
mqttClient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqttClient.connect(MQTT_SERVER, int(MQTT_PORT), 60)

# Register MQTT events
mqttClient.on_connect = mqtt_connected
mqttClient.on_subscribe = mqtt_subscribed
mqttClient.on_message = mqtt_recv_message
i = 0
mqttClient.loop_start()

while True:
    time.sleep(5)
    i+=10
