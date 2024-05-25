# coding=utf-8
import json
import time
from web3 import Web3
# from web3.auto import w3
import paho.mqtt.client as mqtt
from web3.middleware import geth_poa_middleware

# Khai báo thông tin của Smart Contract
config = json.load(open('config.json'))
contract_address = config.get('contract_address')
abi = config.get('contract_abi')

# Khai báo thông tin kết nối RPC với Ethereum node
w3 = Web3(Web3.HTTPProvider("https://bsc-testnet.blockpi.network/v1/rpc/public"))
# w3 = Web3(Web3.HTTPProvider("https://eth-sepolia.public.blastapi.io"))
# w3 = Web3(Web3.WebsocketProvider("wss://bsc-testnet-rpc.publicnode.com"))

w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Khởi tạo đối tượng Contract
contract = w3.eth.contract(address=contract_address, abi=abi)

# Cấu hình MQTT
MQTT_SERVER = "mqttserver.tk"
MQTT_PORT = 1883
MQTT_USERNAME = "innovation"
MQTT_PASSWORD = "Innovation_RgPQAZoA5N"
MQTT_TOPIC_PUB = "/innovation/watermonitoring/test1"

# Hàm kết nối MQTT
def mqtt_connected(client, userdata, flags, rc):
    print("Connected successfully to MQTT broker")

def mqtt_published(client, userdata, mid):
    print("Data published to MQTT broker")

# Tạo MQTT client và kết nối
mqttClient = mqtt.Client()
mqttClient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqttClient.connect(MQTT_SERVER, MQTT_PORT, 60)

mqttClient.on_connect = mqtt_connected
mqttClient.on_publish = mqtt_published
mqttClient.loop_start()

# Hàm xử lý sự kiện blockchain và xuất bản lên MQTT
def handle_event(event):
    data = event['args']
    print("Received event: ", data)
    
    station_data = {
        "station_id": data['_stationId'],
        "gps_longitude": data['_longitude'],
        "gps_latitude": data['_latitude'],
        "sensors": []
    }
    
    for i in range(len(data['_sensorIds'])):
        sensor = {
            "sensor_id": data['_sensorIds'][i],
            "sensor_value": data['_sensorValues'][i],
            "sensor_unit": data['_sensorUnits'][i]
        }
        station_data["sensors"].append(sensor)
    
    payload = json.dumps(station_data)
    mqttClient.publish(MQTT_TOPIC_PUB, payload)
    print("Published data to MQTT:", payload)

def handle_evt(event):
    print("Handling event:", event)

# Hàm để lắng nghe sự kiện
def listen_to_events():
    # event_filter = contract.events.StationDataAdded.create_filter(fromBlock='latest')
    # event_filter = w3.eth.filter({'fromBlock':'latest', 'address':contract_address})
    print("Listening to events...")
    # event_filter = w3.eth.filter('latest')

    # event_filter = contract.events.StationDataAdded.create_filter(fromBlock='latest')
    event_filter = contract.events.StationDataAdded.create_filter(fromBlock='latest')
    print("Event filter created")
    while True:                                                             
        for event in event_filter.get_new_entries():
            # handle_event(event)
            handle_evt(event)
        time.sleep(5)

# Bắt đầu lắng nghe sự kiện
listen_to_events()
