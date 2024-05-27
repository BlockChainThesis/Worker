import paho.mqtt.client as mqtt
import json
import time
import threading
from interact_blockchain import get_station_data, add_stations_data, get_number_of_station, get_sensor_value

MQTT_SERVER = "mqttserver.tk"
MQTT_PORT = 1883
MQTT_USERNAME = "innovation"
MQTT_PASSWORD = "Innovation_RgPQAZoA5N"
MQTT_TOPICS_SUB = ["/innovation/airmonitoring/NBIOTs"]  # Add your topics here

def mqtt_connected(client, userdata, flags, rc):
    print(f"Connected successfully to {userdata['topic']}!")
    client.subscribe(userdata["topic"])

def mqtt_subscribed(client, userdata, mid, granted_qos):
    print(f"Subscribed to {userdata['topic']}!")

def mqtt_recv_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    try:
        data = json.loads(payload)
        print(f"Received JSON from {userdata['topic']}: {data}")
        # Gọi hàm addStationsData trong smart contract
        sensorIds = []
        sensorValues = []
        sensorUinits = []
        for sensor in data["sensors"]:
            sensor_id = sensor["id"]
            if "Relay" in sensor_id:
                continue  # Skip Relay sensors
            sensorIds.append(sensor["id"])
            sensorValues.append(str(sensor["value"]))
            # sensorUinits.append(sensor["sensor_unit"])
            sensorUinits.append("")
            print(sensor["id"], " ", sensor["value"])
        
        # Thực hiện gọi hàm addStationsData từ contract
        receipt = add_stations_data(data["station_id"], "", "", sensorIds, sensorValues, sensorUinits)
        print("Transaction receipt:", receipt)
        
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON message from {userdata['topic']}: ", e)

def start_worker(topic):
    mqttClient = mqtt.Client(userdata={"topic": topic})
    mqttClient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqttClient.connect(MQTT_SERVER, MQTT_PORT, 60)

    # Register MQTT events
    mqttClient.on_connect = mqtt_connected
    mqttClient.on_subscribe = mqtt_subscribed
    mqttClient.on_message = mqtt_recv_message

    mqttClient.loop_forever()

threads = []
for topic in MQTT_TOPICS_SUB:
    thread = threading.Thread(target=start_worker, args=(topic,))
    thread.start()
    threads.append(thread)

# Keep the main thread alive
for thread in threads:
    thread.join()
