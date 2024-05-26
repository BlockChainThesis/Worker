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

def get_controller_value(station_id, controller_id):
    # Gọi hàm getControllerValue từ smart contract
    controller_value = contract.functions.getControllerValue(station_id, controller_id).call()
    return controller_value


# re = update_controller_data("VALVE_0001", "valve_0001", 1)
# print(re)