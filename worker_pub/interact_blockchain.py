from web3 import Web3
import json
from web3.middleware import geth_poa_middleware
from eth_account import Account
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read private key from environment variable
private_key = os.getenv("PRIVATE_KEY")

# Kiểm tra xem private key đã được đọc chưa
if private_key is not None:
    print("Private key:", private_key)
else:
    print("Không tìm thấy private key trong file .env.")

# Khởi tạo đối tượng Account từ private key
account = Account.from_key(private_key)

# Lấy địa chỉ tài khoản
address = account.address
print("Địa chỉ tài khoản:", address)

# Khai báo thông tin của Smart Contract
config = json.load(open('config.json'))
contract_address = config.get('contract_address')
abi = config.get('contract_abi')

# Khai báo thông tin kết nối RPC với Ethereum node
w3 = Web3(Web3.HTTPProvider("https://bsc-testnet.blockpi.network/v1/rpc/public"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Khởi tạo đối tượng Contract
contract = w3.eth.contract(address=contract_address, abi=abi)

def get_station_data(station_id):
    # Gọi hàm getStationData từ smart contract
    station_data = contract.functions.getStationData(station_id).call()
    return station_data

def add_stations_data(station_id, longitude, latitude, sensor_ids, sensor_values, sensor_units):
    # Tạo giao dịch nhưng không gửi đi
    txn_dict = contract.functions.addStationsData(station_id, str(longitude), str(latitude), sensor_ids, sensor_values, sensor_units).build_transaction({
        'chainId': 97,
        'gas': 2000000,
        'gasPrice': w3.to_wei('40', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    # Ký giao dịch
    signed_txn = account.sign_transaction(txn_dict)
    # Gửi giao dịch đã ký đi
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # Đợi cho đến khi giao dịch được xác nhận
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return receipt


def get_number_of_station():
    # Gọi hàm getNumberOfStation từ smart contract
    number_of_station = contract.functions.getNumberOfStation().call()
    return number_of_station

def get_controller_value(station_id, controller_id):
    # Gọi hàm getControllerValue từ smart contract
    controller_value = contract.functions.getControllerValue(station_id, controller_id).call()
    return controller_value

def get_all_station_data():
    # Gọi hàm getAllStationData từ smart contract
    all_station_data = contract.functions.getAllStationData().call()
    return all_station_data

def handle_event(event, mqtt_client, mqtt_topic_pub):
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
    mqtt_client.publish(mqtt_topic_pub, payload)
    print("Published data to MQTT:", payload)



# data = {
#     "station_id": "air_0001",
#     "station_name": "AIR 0001",
#     "gps_longitude": 106.89,
#     "gps_latitude": 10.5,
#     "sensors": [
#         {
#             "sensor_id": "temp_0001",
#             "sensor_name": "Nhiệt Độ",
#             "sensor_value": 130.2,
#             "sensor_unit": "ms/cm"
#         },
#         {
#             "sensor_id": "humi_0001",
#             "sensor_name": "Độ Ẩm",
#             "sensor_value": 73.5,
#             "sensor_unit": "%"
#         },
#         {
#             "sensor_id": "illuminance_0001",
#             "sensor_name": "Độ Sáng",
#             "sensor_value": 112.3,
#             "sensor_unit": "lux"
#         },
#         {
#             "sensor_id": "CO2_0001",
#             "sensor_name": "CO2",
#             "sensor_value": 400.3,
#             "sensor_unit": "ppm"
#         }
#     ]
# }



# # ////// TEST ///////   
# sensorIds = []
# sensorValues = []
# sensorUinits = []
# for sensor in data["sensors"]:
#     sensorIds.append(sensor["sensor_id"])
#     sensorValues.append(str(sensor["sensor_value"]))
#     sensorUinits.append(sensor["sensor_unit"])
#     # print(sensor["sensor_id"]," ",sensor["sensor_value"]," ",sensor["sensor_unit"])

# id = data["station_id"]
# longtitude = data["gps_longitude"]
# latitude = data["gps_latitude"]
# # Thực hiện gọi hàm addStationsData từ contract
# # print(id, " ", longtitude, " ", latitude, " ", sensorIds, " ", sensorValues, " ", sensorUinits)
# # receipt = add_stations_data(id, str(longtitude), str(latitude), sensorIds, sensorValues, sensorUinits)
# # print("Transaction receipt:", receipt)

# # print(get_sensor_value("water_0001", "ec_0001"))
# # print(get_sensor_value("air_0001", "temp_0001"))

# # print(get_station_data("air_0001"))

# print(get_number_of_station())

# print(get_all_station_data())