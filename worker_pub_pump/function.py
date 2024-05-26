# function.py
import paho.mqtt.client as mqtt
import json

# MQTT settings
MQTT_SERVER = "mqttserver.tk"
MQTT_PORT = 1883
MQTT_USERNAME = "innovation"
MQTT_PASSWORD = "Innovation_RgPQAZoA5N"

MQTT_TOPIC_SUB = "/innovation/pumpcontroller/station"
station_data = {}

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
        station_id = data.get("station_id")
        if station_id:
            station_data[station_id] = data
    except json.JSONDecodeError as e:
        print(f"Received non-JSON message: {payload}")

def setup_mqtt_client():
    mqttClient = mqtt.Client()
    mqttClient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqttClient.connect(MQTT_SERVER, int(MQTT_PORT), 60)

    # Register MQTT events
    mqttClient.on_connect = mqtt_connected
    mqttClient.on_subscribe = mqtt_subscribed
    mqttClient.on_message = mqtt_recv_message

    return mqttClient
