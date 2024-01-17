import json
from web3 import Web3
from User import User
import asyncio
import subprocess
import os
import requests
import aiohttp
from certif import Certif

# Initialize user variables
name = "DIMS"
wallet_file = None
user = None
ssn = None

# Connect to the local Ethereum node
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545', request_kwargs={'timeout': 10000}))


# Load contract ABI and address from JSON file
with open("./build/contracts/DataRegistry.json", "r") as json_file:
    contract_data = json.load(json_file)

# Extract contract ABI and address
contract_abi = contract_data["abi"]
#contract_address = contract_data["networks"]["1702292427155"]["address"]
contract_address = '0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab'
private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
# Create a contract instance
data_registry = w3.eth.contract(address=contract_address, abi=contract_abi)

# Set a sample user address for testing
user_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
        

def initialize_user():
    global name, wallet_file, user, ssn

    # Get user input
    print("Enter your name: ", end="")
    name = input()
    print(f"Hello {name}")

    print("Enter your ssn: ", end="")
    ssn = int(input())
    print(f"Your SSN: {ssn}")

    print("Enter your data: ", end="")
    data = input()


    try:
        # Create User instance and encrypt data
        user = User(name=name, ssn=ssn, data=data)
        user.encrypt_data()
        print("Wallet Loaded")

    except Exception as e:
        print("Error in loading wallet")
        raise e

async def send_transaction_async(chunk, nonce, gas_price, gas_limit, chain_id):
    transaction = {
        'to': user_address,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': nonce,
        'data': chunk.hex(),
        'chainId': chain_id,
    }
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)
    payload = {
        'jsonrpc': '2.0',
        'method': 'eth_sendRawTransaction',
        'params': [signed_transaction.rawTransaction.hex()],
        'id': 1,
    }
    response = requests.post('http://127.0.0.1:8545', json=payload)
    return response.json().get('result')

async def send_file_to_blockchain(file_path):
    if not file_path:
        print("File path not provided.")
        return

    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    nonce = w3.eth.get_transaction_count(user_address)
    gas_price = w3.eth.gas_price
    gas_limit = 90000000  # Adjust as needed
    chain_id = w3.eth.chain_id

    chunk_size = len(file_content) // 100
    tasks = []

    for i in range(100):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < 99 else len(file_content)
        chunk = file_content[start:end]

        # Print the generated transaction data

        tasks.append(send_transaction_async(chunk, nonce + i, gas_price, gas_limit, chain_id))

    # Execute all tasks asynchronously
    responses = await asyncio.gather(*tasks)

    # Wait for transactions to be mined
    await wait_for_transactions_mined(responses)

    print("All transactions sent to the blockchain successfully.")


async def wait_for_transactions_mined(tx_hashes):
    for tx_hash in tx_hashes:
        if tx_hash is None:
            continue

        while True:
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt and receipt['blockNumber']:
                    print(f"Transaction {tx_hash} mined in block {receipt['blockNumber']}")
                    break
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error getting receipt for {tx_hash}: {e}")
                await asyncio.sleep(1)


def is_contract_deployed(address):
    try:
        code = w3.eth.get_code(address)
        return code and code != "0x"
    except Exception as e:
        print(f"Error checking if contract is deployed: {e}")
        return False



async def get_latest_transaction_hashes():
    try:
        transaction_hashes = []

        for latest_block_number in range(0, 101):
            # Get transactions from the latest block
            block = w3.eth.get_block(latest_block_number, True)


            if block and 'transactions' in block:
                # Extract all transaction hashes from the block
                transaction_hashes.extend([tx['hash'].hex() for tx in block['transactions']])
            else:
                print(f"No transactions found in block {latest_block_number}.")

        return transaction_hashes

    except Exception as e:
        print(f"Error while retrieving transactions: {e}")
        return []


async def get_file_from_blockchain():
    transaction_hashes = await get_latest_transaction_hashes()
    for tx_hash in transaction_hashes:
        # JSON-RPC request payload
        payload = {
            'jsonrpc': '2.0',
            'method': 'eth_getTransactionByHash',
            'params': [tx_hash],
            'id': 1,
        }

        try:
            # Make the JSON-RPC request
            response = requests.post('http://127.0.0.1:8545', json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            result = response.json().get('result')

            if result:
                # Extract the input data from the transaction
                input_data = result.get('input')
                decoded_input_data = bytes.fromhex(input_data[2:])
                file_path = "unipi.hvt"  # Generate a unique file name

                # Write the binary data to a file
                with open(file_path, "ab") as file:
                    file.write(decoded_input_data)

            else:
                print(f"Transaction {tx_hash} not found.")

        except requests.exceptions.RequestException as e:
            print(f"Error during JSON-RPC request: {e}")



def create_vm(vm_name, remote, hook, ipv4, ipv4_gateway, port, tls, ssh_key, ssh_authenticator):
    global w3, vm_controller, user_address

    # Get nonce and chain ID
    nonce = w3.eth.get_transaction_count(user_address)
    chain_id = w3.eth.chain_id

    # Encode the function call
    transaction = vm_controller.functions.createVM(
        vm_name,
        remote,
        hook,
        ipv4,
        ipv4_gateway,
        port,
        tls,
        ssh_key,
        ssh_authenticator
    ).build_transaction({
        'gas': 2000000,
        'gasPrice': 20000000000,
        'from': user_address,
        'nonce': nonce,
        'chainId': chain_id
    })

    # Send transaction
    tx_hash = w3.eth.send_transaction(transaction)
    print(f"VM creation initiated. Transaction Hash: {tx_hash.hex()}")

def generate_ca():
    # Generate the root CA certificate and server keypair
    Certif.generate_ca()

def server_start_endpoint():
    subprocess.run(["albatross-tls-endpoint", "cacert.pem", "server.pem", "server.key"])
def Destroy_vm() : 
    # Destroying the vm 
    subprocess.run(["albatross-client", "destroy", "unipi"])

def user_add_policy():
    # User generates a signing request to allow a memory of 1024MB to run 16 unikernels on CPU IDs 0 and 1
    Certif.user_add_policy()

def ca_sign_user_request():
    # CA signs the user's request
    Certif.ca_sign_user_request()


def intermediate_sign_unipi_request():
    # Intermediate CA signs the request
    subprocess.run(["albatross-client", "sign", "key/user.pem", "db", "key/user.key", "key/user.req"])

def client_create_remote_unipi():
    # Client sends the signed request to the server
    subprocess.run(["albatross-client", "certificate", "key/cacert.pem", "key/unipi.pem", "key/unipi.key", "--destination", "10.0.0.10/24"])

async def sign_vm():
    # Assuming you have functions for certificate generation and signing
    generate_ca()
    user_add_policy()
    ca_sign_user_request()
    # intermediate_sign_unipi_request()
    # client_create_remote_unipi()

async def create_vm_with_unipi():
    
    await get_file_from_blockchain()
    ssh_key = "ed25519:2JueTxGu7icIG6jpfFDl4AEr4L6zTUbMkS+e2vW4B/8="
    ssh_authenticator = "SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"

    # Execute the albatross-client command to create a VM with unipi.hvt
    subprocess.run([
        "sudo",
        "albatross-client", "create", "unipi", "unipi.hvt",
        "--ca=key/user.pem",
        "--ca-key=key/user.pem",
        "--server-ca=key/cacert.pem",
        "--net=service",
        "--arg=--ipv4=10.0.0.10/24",
        "--arg=--ipv4-gateway=10.0.0.254",
        "--arg=--port=8443",
        "--arg=--remote=https://github.com/ahmed1abid/DDIwithIPFS.git",
        "--arg=--ssh-authenticator=" + ssh_authenticator,
        "--arg=--ssh-key=" + ssh_key,
        "--arg=--tls=false",
        "--arg=--hook=/updatewebhook",
        "--arg=-l debug",
        "--arg=--ipv4-only=true"

    ])
    os.remove('unipi.hvt')

if __name__ == "__main__":
    # Enter the main loop
    while True:
        print(f"# {name}> ", end="")
        inp_list = input().split(' ')

        # Handle user commands
        if inp_list[0] in ['initialize', 'init']:
            if inp_list[1] in ['user']:
                initialize_user()


        elif inp_list[0] in ['destroy']:
            if inp_list[1] in ['vm']:
                Destroy_vm()
            else:
                print("there si a problem with the vm : either it's not creater or we dont have acces to it to delete it")


        elif inp_list[0] in ['send', 'store', 'upload']:
            if inp_list[1] in ['data']:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(send_file_to_blockchain('/home/ahmed/Desktop/cyber/idenity/unipi/dist/unipi.hvt'))
            else:
                print("User address is not set. Make sure to set it to your Ethereum address.")

        elif inp_list[0] in ['get']:
            if inp_list[1] in ['data']:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(get_file_from_blockchain())
        elif inp_list[0] in ['sign']:
            if inp_list[1] in ['vm']:
                asyncio.run(sign_vm())

        elif inp_list[0] in ['create']:
            if inp_list[1] in ['vm']:
                asyncio.run(create_vm_with_unipi())


            else:
                print("User address is not set. Make sure to set it to your Ethereum address.")
