import os
import json
import aiohttp
from termcolor import colored
from web3 import Web3
from pinatapy import PinataPy
from dotenv import load_dotenv
from User import User

# Load sensitive information from environment variables
load_dotenv()
pinata_api_key = os.environ.get('PinataAPIKey')
pinata_secret_api_key = os.environ.get('PinataAPISecret')

# Load the contract ABI and address from the JSON file
with open("./build/contracts/DataRegistry.json", "r") as json_file:
    contract_data = json.load(json_file)

# Extract the contract ABI and address
contract_abi = contract_data["abi"]
contract_address = contract_data["networks"]["5777"]["address"]

# Connect to the Pinata IPFS cloud service
pinata = PinataPy(pinata_api_key, pinata_secret_api_key)

# Connect to the local Ethereum node (Ganache)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Main function
async def main():
    # Select a specific user address for testing (use one of the sample addresses)
    user_address = await get_user_address(w3)

    # User object
    user = None

    while True:
        print("# DIMS> ", end="")
        inp = input()
        inp_list = inp.split(' ')

        if inp_list[0] in ['initialize', 'init']:
            if inp_list[1] in ['user']:
                user = initialize_user()

        elif inp_list[0] in ['display', 'show', 'view']:
            if inp_list[1] in ['user_data']:
                display_user_data(user)

            elif inp_list[1] in ['data']:
                await display_data(user.data)

        elif inp_list[0] in ['send', 'store', 'upload']:
            if inp_list[1] in ['data']:
                await store_data(user, contract_abi, contract_address, user_address)

# Function to initialize the user
def initialize_user():
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
        return user

    except Exception as e:
        print("Error in loading wallet")
        raise e

# Function to display user data
def display_user_data(user):
    if user is None:
        print('User is None, use "init user"')
        return

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

# Function to display data from IPFS
async def display_data(ipfs_hash):
    if ipfs_hash:
        retrieved_user_data = await get_from_ipfs_async(ipfs_hash)
        print("Retrieved user data from IPFS:", retrieved_user_data)
    else:
        print("Retrieved user data from IPFS: is not there")

# Function to store data on the blockchain
async def store_data(user, contract_abi, contract_address, user_address):
    if user.data:
        data_to_store = "name  : " + user.name + "   ssn   :  " + str(user.ssn) + " data   : " + user.data
        if data_to_store:
            ipfs_hash = await upload_to_ipfs_async(data_to_store, pinata)
            print("User data added to IPFS. IPFS Hash:", ipfs_hash)

            # Convert ipfs_hash to string
            ipfs_hash = str(ipfs_hash)

            # Fetch the latest nonce and chain ID
            nonce = w3.eth.get_transaction_count(user_address)
            chain_id = w3.eth.chain_id

            # Encode the function call
            transaction = w3.eth.contract(address=contract_address, abi=contract_abi).functions.storeData(ipfs_hash).build_transaction({
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

# Function to get the user's Ethereum address from Ganache
async def get_user_address(w3):
    accounts = w3.eth.accounts
    print(accounts)
    return accounts[0]

# Upload data to IPFS using Pinata API
async def upload_to_ipfs_async(data, pinata):
    temp_file_path = "temp_data.json"
    with open(temp_file_path, "w") as json_file:
        json.dump(data, json_file)

    try:
        result =  pinata.pin_file_to_ipfs(temp_file_path)
        return result
    finally:
        os.remove(temp_file_path)

# Retrieve data from IPFS using Pinata API
async def get_from_ipfs_async(hash):
    gateway = "https://ipfs.io/ipfs/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=gateway + hash) as response:
            return await response.text()
        

# Run the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
