import os
from web3 import Web3
from dotenv import load_dotenv
from colorama import init, Fore, Style
import random
import time  # Import time module for delay

# Print header
print(Fore.GREEN + "+-----------------------------------------+")
print(Fore.GREEN + "            Units Network Testnet")
print(Fore.GREEN + "          Modif from HappyCuanAirdrop")
print(Fore.GREEN + "+-----------------------------------------+")

def send_ether(w3, private_key, recipients):
    # Disable automatic gas price checking
    w3.middleware_onion.clear()

    # Define a gas price (e.g., 50 Gwei)
    gas_price = w3.to_wei('0.00111177', 'gwei')

    # Define the gas limit for a simple Ether transfer
    gas_limit = 60000

    # Get the sender's address from private key
    sender_address = w3.eth.account.from_key(private_key).address

    # Get the sender's nonce
    nonce = w3.eth.get_transaction_count(sender_address)

    # Initialize total gas needed
    total_gas = 0

    # Collect transaction data for each recipient with a sequence number
    txs = []
    tx_sequence_number = 0
    for recipient_address, amount in recipients.items():
        recipient_address_checksum = Web3.to_checksum_address(recipient_address)
        amount_in_wei = w3.to_wei(amount, 'ether')
        tx = {
            'to': recipient_address_checksum,
            'value': amount_in_wei,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': w3.eth.chain_id
        }
        txs.append((tx_sequence_number, tx))
        total_gas += gas_limit
        nonce += 1
        tx_sequence_number += 1

    # Verify if the sender has enough balance for the total transaction cost
    sender_balance = w3.eth.get_balance(sender_address)
    total_cost = total_gas * gas_price + sum(w3.to_wei(amount, 'ether') for amount in recipients.values())
    print(Fore.CYAN + f"Sender balance: {Web3.from_wei(sender_balance, 'ether')} ETH")
    print(Fore.CYAN + f"Total cost: {Web3.from_wei(total_cost, 'ether')} ETH")
    if sender_balance < total_cost:
        raise ValueError(Fore.RED + "Insufficient balance for transactions and gas fees.")

    # Sign and send transactions
    signed_txs = []
    for tx_sequence, tx in txs:
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        signed_txs.append((tx_sequence, signed_tx))

    for tx_sequence, signed_tx in signed_txs:
        while True:
            try:
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print(Fore.GREEN + f"Transaction {tx_sequence} successfully sent. Transaction hash: {tx_hash.hex()}")
                break
            except ValueError as e:
                if "nonce too low" in str(e).lower():
                    print(Fore.YELLOW + f"Nonce too low for transaction {tx_sequence}. Incrementing nonce and retrying...")
                    tx['nonce'] = w3.eth.get_transaction_count(sender_address)
                    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                elif "known transaction" in str(e).lower():
                    print(Fore.YELLOW + f"Transaction {tx_sequence} is already known. Skipping...")
                    break  # Skip to the next transaction
                elif "replacement transaction underpriced" in str(e).lower():
                    print(Fore.YELLOW + f"Transaction {tx_sequence} underpriced. Retrying with higher gas price...")
                    tx['gasPrice'] = gas_price * 2  # Double the gas price
                    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                else:
                    print(Fore.RED + f"Error sending transaction {tx_sequence}: {e}")
                    raise e
                time.sleep(5)  # Wait for a few seconds before retrying

# Load environment variables from .env file
load_dotenv()

# Initialize Web3 and other configurations
rpc_url = os.getenv("RPC_URL")  # Ensure this matches your RPC server address
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

# Loop through private keys and send transactions
for private_key in private_keys:
    send_ether(w3, private_key, recipients)
