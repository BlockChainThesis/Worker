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
w3 = Web3(Web3.HTTPProvider("https://bsc-testnet.blockpi.network/v1/rpc/public"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Khởi tạo đối tượng Contract
contract = w3.eth.contract(address=contract_address, abi=abi)

def update_controller_data(station_id, controller_id, value):
    # Tạo giao dịch nhưng không gửi đi
    txn_dict = contract.functions.updateControllerValue(station_id, controller_id, str(value)).build_transaction({
        'chainId': 97,
        'gas': 2000000,
        'gasPrice': w3.to_wei('5', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    # Ký giao dịch
    signed_txn = account.sign_transaction(txn_dict)
    # Gửi giao dịch đã ký đi
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # Đợi cho đến khi giao dịch được xác nhận
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def update_controller_data_batch(station_ids, controller_ids, values):
    # Tạo giao dịch nhưng không gửi đi
    txn_dict = contract.functions.updateControllerValueBatch(station_ids, controller_ids, values).build_transaction({
        'chainId': 97,
        'gas': 10000000,
        'gasPrice': w3.to_wei('5.05', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    # Ký giao dịch
    signed_txn = account.sign_transaction(txn_dict)
    # Gửi giao dịch đã ký đi
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # Đợi cho đến khi giao dịch được xác nhận
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

# Hàm để thêm giao dịch vào Redis
def add_transaction_off_chain(station_id, controller_id, value):
    transaction_count = r.llen('controller_transactions')
    transaction_data = json.dumps({
        "stationId": station_id,
        "controllerId": controller_id,
        "value": str(value),
    })
    if transaction_count < 20:
        r.rpush('controller_transactions', transaction_data)
        print(f"Transaction added to Redis. Total transactions: {transaction_count + 1}")
    else:
        print("20 transactions reached. Sending to blockchain.")
        send_transactions_to_blockchain()

# Hàm để gửi các giao dịch từ Redis lên blockchain
def send_transactions_to_blockchain():
    transactions = [json.loads(r.lindex('controller_transactions', i)) for i in range(r.llen('controller_transactions'))]

    if transactions:
        station_ids = [t['stationId'] for t in transactions]
        controller_ids = [t['controllerId'] for t in transactions]
        values = [t['value'] for t in transactions]

    receipt = update_controller_data_batch(station_ids, controller_ids, values)
    # Xóa các giao dịch trong Redis sau khi gửi thành công
    r.delete('controller_transactions')
    print(f"Receipt: {receipt}")

def get_controller_value(station_id, controller_id):
    # Gọi hàm getControllerValue từ smart contract
    controller_value = contract.functions.getControllerValue(station_id, controller_id).call()
    return controller_value


# for i in range(21):
#     station_id = "Station" + str(i)
#     controller_id = "Controller" + str(i)
#     value = "Value" + str(i)
#     add_transaction_off_chain(station_id, controller_id, value)