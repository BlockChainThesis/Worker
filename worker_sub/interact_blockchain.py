from web3 import Web3
import json
from web3.middleware import geth_poa_middleware
from eth_account import Account
import os
from dotenv import load_dotenv
import redis

# Connect Redis
r = redis.Redis(host='localhost', port=6379, db=0)

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
web3 = Web3(Web3.HTTPProvider("https://bsc-testnet.blockpi.network/v1/rpc/public"))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Khởi tạo đối tượng Contract
contract = web3.eth.contract(address=contract_address, abi=abi)

def get_station_data(station_id):
    # Gọi hàm getStationData từ smart contract
    station_data = contract.functions.getStationData(station_id).call()
    return station_data

def add_stations_data_batch(station_ids, longitudes, latitudes, sensor_ids_list, sensor_values_list, sensor_units_list):
    # Tạo giao dịch nhưng không gửi đi
    transaction = contract.functions.addStationsDataBatch(station_ids, longitudes, latitudes, sensor_ids_list, sensor_values_list, sensor_units_list).build_transaction({
        'chainId': 97,  # ID của BNB Testnet
        'gas': 10000000,
        'gasPrice': web3.to_wei('5.05', 'gwei'),
        'nonce': web3.eth.get_transaction_count(account.address)
    })

    # Ký giao dịch
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

    # Gửi giao dịch và chờ xác nhận
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    return receipt

# Hàm để thêm giao dịch vào Redis
def add_transaction_off_chain(station_id, longitude, latitude, sensor_ids, sensor_values, sensor_units):
    transaction_count = r.llen('transactions')
    transaction_data = json.dumps({
        "stationId": station_id,
        "longitude": longitude,
        "latitude": latitude,
        "sensorIds": sensor_ids,
        "sensorValues": sensor_values,
        "sensorUnits": sensor_units
    })
    if transaction_count < 20:
        r.rpush('transactions', transaction_data)
        print(f"Transaction added to Redis. Total transactions: {transaction_count + 1}")
    else:
        print("20 transactions reached. Sending to blockchain.")
        send_transactions_to_blockchain()

# Hàm để gửi các giao dịch từ Redis lên blockchain
def send_transactions_to_blockchain():
    transactions = [json.loads(r.lindex('transactions', i)) for i in range(r.llen('transactions'))]

    if transactions:
        station_ids = [t['stationId'] for t in transactions]
        longitudes = [t['longitude'] for t in transactions]
        latitudes = [t['latitude'] for t in transactions]
        sensor_ids_list = [t['sensorIds'] for t in transactions]
        sensor_values_list = [t['sensorValues'] for t in transactions]
        sensor_units_list = [t['sensorUnits'] for t in transactions]

    receipt = add_stations_data_batch(station_ids, longitudes, latitudes, sensor_ids_list, sensor_values_list, sensor_units_list)
    # Xóa các giao dịch trong Redis sau khi gửi thành công
    r.delete('transactions')
    print(f"Receipt: {receipt}")


def get_number_of_station():
    # Gọi hàm getNumberOfStation từ smart contract
    number_of_station = contract.functions.getNumberOfStation().call()
    return number_of_station

def get_sensor_value(station_id, sensor_id):
    # Gọi hàm getSensorValue từ smart contract
    sensor_value = contract.functions.getSensorValue(station_id, sensor_id).call()
    return sensor_value

def get_all_station_data():
    # Gọi hàm getAllStationData từ smart contract
    all_station_data = contract.functions.getAllStationData().call()
    return all_station_data

# # Ví dụ: Thêm các giao dịch off-chain
# for i in range(21):
#     add_transaction_off_chain(f'station_{i+1}', f'longitude_{i+1}', f'latitude_{i+1}', [f'sensor_{i+1}'], [f'value_{i+1}'], [f'unit_{i+1}']) 

