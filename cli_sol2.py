import json
import yaml
from termcolor import colored
from web3 import Web3
from User import User

def initialize_user():
    global name, wallet_file, user, ssn
    print("Enter your name: ", end="")
    name = input()
    print(f"Hello {colored(name, 'blue')}")
    print("Please give your wallet file path: ", end="")
    wallet_file = input() or "wallet.yaml"

    print("Enter your ssn: ", end="")
    ssn = int(input())
    print(f"Your SSN: {colored(ssn, 'blue')}")

    print("Enter your data: ", end="")
    data = input()

    try:
        user = User(name=name, wallet_file=wallet_file, ssn=ssn, data=data)
        user.encrypt_data()
        print("Wallet Loaded")

    except Exception as e:
        print("Error in loading wallet")
        raise e

def display_user_data():
    global user
    if user is None:
        print('User is None, use "init user"')
        return

    print(f"User Name: {user.name}")
    print(f"User SSN: {user.ssn}")

    if user.wallet:
        print(f"Certificates available: {list(user.wallet.keys())}")
        for cert_name, cert_file in user.wallet.items():
            print(f"*********{colored('CERTIFICATE', 'red')}: {colored(cert_name, 'yellow')} ***********\n")
            cert_data = yaml.safe_load(open(cert_file))
            for attr, value in cert_data.items():
                if attr != 'Attributes':
                    print(colored(f"{attr}: {str(value)}", 'blue') + colored(f"{attr}: {str(value)}", 'green'))
                else:
                    for ind_attr, ind_value in value.items():
                        print('\t' + colored(f"{ind_attr}: {str(ind_value)}", 'blue') + f'{ind_attr}: {str(ind_value)}', 'green')
            print("\n*************************************************\n")

def send_file_to_blockchain(file_path):
    global user, w3, data_registry, user_address

    if not file_path:
        print("File path not provided.")
        return

    try:
        with open(file_path, 'rb'):
            pass  # Just check if the file exists, don't read its content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    nonce = w3.eth.get_transaction_count(user_address)
    chain_id = w3.eth.chain_id

    # Encode the function call
    transaction = data_registry.functions.storeFile(file_path).build_transaction({
        'gas': 2000000,
        'gasPrice': 20000000000,
        'from': user_address,
        'nonce': nonce,
        'chainId': chain_id
    })

    tx_hash = w3.eth.send_transaction(transaction)
    print(f"File sent to the blockchain. Transaction Hash: {tx_hash.hex()}")

def create_vm(vm_name, remote, hook, ipv4, ipv4_gateway, port, tls, ssh_key, ssh_authenticator):
    global w3, vm_controller, user_address

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

    tx_hash = w3.eth.send_transaction(transaction)
    print(f"VM creation initiated. Transaction Hash: {tx_hash.hex()}")


if __name__ == "__main__":
    # Load the contract ABI and address from the JSON file
    with open("./build/contracts/DataRegistry.json", "r") as json_file:
        contract_data = json.load(json_file)

    # Extract the contract ABI and address
    contract_abi = contract_data["abi"]
    contract_address = contract_data["networks"]["5777"]["address"]

    name = "DIMS"
    wallet_file = None
    user = None
    ssn = None
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    data_registry = w3.eth.contract(address=contract_address, abi=contract_abi)

    # Select a specific user address for testing (use one of the sample addresses)
    user_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"

    while True:
        print(f"# {name}> ", end="")
        inp_list = input().split(' ')

        if inp_list[0] in ['initialize', 'init']:
            if inp_list[1] in ['user']:
                initialize_user()

        elif inp_list[0] in ['display', 'show', 'view']:
            if inp_list[1] in ['user_data']:
                display_user_data()

        elif inp_list[0] in ['send', 'store', 'upload']:
            if inp_list[1] in ['data']:
                send_file_to_blockchain(user.data)
            else:
                print("User address is not set. Make sure to set it to your Ethereum address.")
        elif inp_list[0] in ['create']:
            if inp_list[1] in ['vm']:
                create_vm(
                        "VMNAME",
                        "https://github.com/ahmed1abid/DDIwithIPFS.git",
                        "/updatewebhook",
                        "10.0.0.10/24",
                        "10.0.0.254",
                        1234,
                        False,
                        "ed25519:2JueTxGu7icIG6jpfFDl4AEr4L6zTUbMkS+e2vW4B/8=",
                        "SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"
                    )
            else:
                print("User address is not set. Make sure to set it to your Ethereum address.")