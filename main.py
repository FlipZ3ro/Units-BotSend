import os
from web3 import Web3
from dotenv import load_dotenv
from contract_interaction import send_ether
import random

# Print header
print("+-----------------------------------------+")
print("            Units Network Testnet")
print("          Modif from HappyCuanAirdrop")
print("+-----------------------------------------+")

# Load environment variables from .env file
load_dotenv()

# Initialize Web3 and other configurations
rpc_url = "https://rpc-testnet.unit0.dev"  # Replace with your RPC URL
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Load private keys from .env file
private_keys_str = os.getenv("PRIVATE_KEYS")
private_keys = private_keys_str.split(',')

# Prompt user for the number of transactions to send
num_transactions = int(input("Enter the number of transactions you want to send: "))

# Generate random recipient addresses and the amount of Ether to send to each (in Ether)
recipients = {}
for i in range(num_transactions):
    new_account = w3.eth.account.create()
    recipient_address = new_account.address
    amount = round(random.uniform(0.00000001, 0.00000001), 8)  # Random amount between 0.00001 and 0.0001 Ether
    recipients[recipient_address] = amount
    print(f"Generated address {i+1}: {recipient_address}")

# Call the send_ether function for each private key
for private_key in private_keys:
    sender_address = w3.eth.account.from_key(private_key).address
    print(f"Sending transactions from address: {sender_address}")
    send_ether(w3, sender_address, private_key, recipients)
