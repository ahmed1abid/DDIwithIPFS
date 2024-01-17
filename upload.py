# def get_file_from_blockchain():
#     try:
#         # Check if the contract is deployed
#         if not is_contract_deployed(contract_address):
#             print("Contract not deployed. Please deploy the contract first.")
#             return None

#         # Call the getStoredFileData function
#         (sender_address, file_content_length) = data_registry.functions.getStoredFileData().call()

#         # Call the getStoredFile function to get the file content
#         stored_file_content_bytes = data_registry.functions.getStoredFile().call()

#         # Convert bytes to a hexadecimal string
#         stored_file_content_hex = binascii.hexlify(stored_file_content_bytes).decode()

#         # Ensure the hex string has an even length before converting
#         stored_file_content_hex = '0' + stored_file_content_hex if len(stored_file_content_hex) % 2 != 0 else stored_file_content_hex

#         # Convert hexadecimal string to binary
#         stored_file_content = binascii.unhexlify(stored_file_content_hex)

#         # Save the binary content to a file
#        

#         print(f"File retrieved from sender {sender_address} with length {file_content_length} and saved successfully to {file_path}.")

#     except Exception as e:
#         print("Error retrieving file from the blockchain.")
#         print(e)




# def send_file_to_blockchain(file_path):
#     global user, w3, data_registry, user_address

#     # Check if file path provided
#     if not file_path:
#         print("File path not provided.")
#         return

#     try:
#         # Read the file content as bytes
#         with open(file_path, 'rb') as file:
#             file_content = file.read()

#     except FileNotFoundError:
#         print(f"File not found: {file_path}")
#         return

#     # Get nonce and chain ID


#     # Divide the file into 5 chunks
#     chunk_size = len(file_content) // 100
#     for i in range(100):
#         nonce = w3.eth.get_transaction_count(user_address)
#         chain_id = w3.eth.chain_id
#         start = i * chunk_size
#         end = (i + 1) * chunk_size if i < 99 else len(file_content)
#         chunk = file_content[start:end]
#         print(f"Chunk {i + 1} length: {len(chunk)}")
#         # Encode the function call for each chunk
#         transaction = data_registry.functions.storeFile(chunk).build_transaction({
#             'gas': 9000000000,  
#             'gasPrice': 20000000000,
#             'from': user_address,
#             'nonce': nonce,
#             'chainId': chain_id
#         })

#         # Send transaction
#         tx_hash = w3.eth.send_transaction(transaction)
#         print(f"Chunk {i + 1} sent to the blockchain. Transaction Hash: {tx_hash}")

#    print("File sent to the blockchain successfully.")


# def generate_ca():
#     # Generate the root CA certificate and server keypair
#     subprocess.run(["albatross-client", "generate", "ca", "db"])

# def server_start_endpoint():
#     # Server starts the endpoint using the server keypair and the root CA certificate
#     subprocess.run(["albatross-tls-endpoint", "cacert.pem", "server.pem", "server.key"])

# def user_add_policy():
#     # User generates a signing request to allow a memory of 1024MB to run 16 unikernels on CPU IDs 0 and 1
#     subprocess.run(["albatross-client", "add-policy", "user", "16", "--mem", "1024", "--cpu", "0", "--cpu", "1", "--csr"])

# def ca_sign_user_request():
#     # CA signs the user's request
#     subprocess.run(["albatross-client", "sign", "cacert.pem", "db", "ca.key", "user.req"])

