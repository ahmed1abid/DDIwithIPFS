import subprocess
import os
import json
from termcolor import colored
from web3 import Web3
from dotenv import load_dotenv
from User import User

# Load the contract ABI and address from the JSON file
with open("./build/contracts/DataRegistry.json", "r") as json_file:
    contract_data = json.load(json_file)

user_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"

# Extract the contract ABI and address
contract_abi = contract_data["abi"]
contract_address = contract_data["networks"]["5777"]["address"]

name = "DIMS"
wallet_file = None
user = "ahmed"
ssn = 462626
data = "test"
user = User(name=name, wallet_file=wallet_file, ssn=ssn, data=data)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
data_registry = w3.eth.contract(address=contract_address, abi=contract_abi)

# Function to upload data to IPFS using curl
def upload_to_ipfs_curl(data):
    # Serialize data to a JSON file
    temp_file_path = "temp_data.json"
    with open(temp_file_path, "w") as json_file:
        json.dump(data, json_file)

    try:
        # Build the curl command
        curl_command = (
            f'curl -X POST -F file=@{temp_file_path} '
            'http://127.0.0.1:5001/api/v0/add?quieter=true&silent=true&progress=true&trickle=true'
            '&only-hash=true&wrap-with-directory=true&chunker=size-262144&raw-leaves=true&nocopy=true&fscache=true'
            '&cid-version=0&hash=sha2-256&inline=true&inline-limit=32&pin=true&to-files=true'
        )

        # Execute the curl command using subprocess
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)

        # Parse the result to get the IPFS hash
        ipfs_hash = json.loads(result.stdout)["Hash"]

        return ipfs_hash
    finally:
        # Delete the local JSON file
        os.remove(temp_file_path)

# Function to retrieve data from IPFS using curl
def get_from_ipfs_curl(hash):
    # Build the curl command
    curl_command = f'curl -X POST "http://127.0.0.1:5001/api/v0/cat?arg={hash}"'

    # Execute the curl command using subprocess
    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)

    return result.stdout

# New Functions for IPFS API commands

def show_bitswap_stats():
    response = subprocess.run(['ipfs', 'bitswap', 'stat'], capture_output=True, text=True)
    print("Bitswap Agent Stats:", response.stdout)

def get_local_node_info():
    response = subprocess.run(['ipfs', 'id'], capture_output=True, text=True)
    print("Local Node Information:", response.stdout)

def get_block_info(block_cid):
    response = subprocess.run(['ipfs', 'block', 'stat', block_cid], capture_output=True, text=True)
    print("Block Information for {}: {}".format(block_cid, response.stdout))

def get_repo_info():
    response = subprocess.run(['ipfs', 'repo', 'stat'], capture_output=True, text=True)
    print("Local Repository Information:", response.stdout)

# Main Loop
while True:
    print("# " + name + "> ", end="")
    inp = input()
    inp_list = inp.split(' ')

    if inp_list[0] in ['initialize', 'init']:
        if inp_list[1] in ['user']:
            print("Enter your name: ", end="")
            name = input()
            print("Hello " + colored(name, 'blue'))
            print("Please give your wallet file path: ", end="")
            wallet_file = input() or "wallet.yaml"

            print("Enter your ssn: ", end="")
            ssn = int(input())
            print("Your SSN: " + colored(ssn, 'blue'))

            print("Enter your data: ", end="")
            data = input()

            try:
                user = User(name=name, wallet_file=wallet_file, ssn=ssn, data=data)
                user.encrypt_data()
                print("Wallet Loaded")

            except Exception as e:
                print("Error in loading wallet")
                raise e

    if inp_list[0] in ['display', 'show', 'view']:
        if inp_list[1] in ['user_data']:
            if user is None:
                print('User is None, use "init user"')
                continue

            print("User Name: " + user.name)
            print("User SSN: " + str(user.ssn))

            if user.wallet:
                print("Certificates available: " + str(user.wallet.keys()))
                for cert_name in user.wallet.keys():
                    print("*********" + colored('CERTIFICATE', 'red') + ": " + colored("{}".format(cert_name), 'yellow') + " ***********\n")
                    cert_file = user.wallet[cert_name]
                    cert_data = json.safe_load(open(cert_file))
                    for attr, value in cert_data.items():
                        if attr != 'Attributes':
                            print(colored(attr, 'blue') + " : " + colored(str(value), 'green'))
                        else:
                            for ind_attr, ind_value in value.items():
                                print('\t' + colored(ind_attr, 'blue') + ' : ' + colored(str(ind_value), 'green'))
                    print("\n*************************************************\n")

    if inp_list[0] in ['send', 'store', 'upload']:
        if inp_list[1] in ['data']:
            if user.data:
                data_to_store = "name  : " + user.name + "   ssn   :  " + str(user.ssn) + " data   : " + user.data
                if data_to_store:
                    # Upload data to IPFS using curl
                    ipfs_hash = upload_to_ipfs_curl(data_to_store)
                    print("User data added to IPFS. IPFS Hash:", ipfs_hash)

                    # Convert ipfs_hash to string
                    ipfs_hash = str(ipfs_hash)

                    # Fetch the latest nonce and chain ID
                    nonce = w3.eth.get_transaction_count(user_address)
                    chain_id = w3.eth.chain_id

                    # Encode the function call
                    transaction = data_registry.functions.storeData(ipfs_hash).build_transaction({
                        'gas': 2000000,
                        'gasPrice': 20000000000,
                        'from': user_address,
                        'nonce': nonce,
                        'chainId': chain_id
                    })

                    tx_hash = w3.eth.send_transaction(transaction)
                    print("User data sent to the blockchain. Transaction Hash:", tx_hash.hex())

                else:
                    print("No user data to send.")
            else:
                print("User address is not set. Make sure to set it to your Ethereum address.")

    if inp_list[0] in ['display', 'show', 'view']:
        if inp_list[1] in ['data']:
            if len(inp_list) > 2 :
                 ipfs_hash = inp_list[2]
                 retrieved_user_data = get_from_ipfs_curl(ipfs_hash)
                 print("Retrieved user data from IPFS:", retrieved_user_data)
            else : 
                if ipfs_hash:
                    # Retrieve user data from IPFS using curl
                    retrieved_user_data = get_from_ipfs_curl(ipfs_hash)
                    print("Retrieved user data from IPFS:", retrieved_user_data)
                else:
                    print("Retrieved user data from IPFS is not there ")


    # New conditions for IPFS API commands
    if inp_list[0] in ['show', 'stats']:
        if inp_list[1] in ['bitswap']:
            show_bitswap_stats()

    if inp_list[0] in ['get', 'info']:
        if inp_list[1] in ['node']:
            get_local_node_info()

    if inp_list[0] in ['get', 'info']:
        if inp_list[1] in ['block']:
            block_cid = inp_list[2]
            get_block_info(block_cid)

    if inp_list[0] in ['get', 'info']:
        if inp_list[1] in ['repo']:
            get_repo_info()
