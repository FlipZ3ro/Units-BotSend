import os
import random
from web3 import Web3
from dotenv import load_dotenv

def check_balance(w3, address):
    balance = w3.eth.get_balance(address)
    return w3.fromWei(balance, 'ether')

def send_ether(w3, sender_address, private_key, recipients):
    # Disable automatic gas price checking
    w3.middleware_onion.clear()

    # Define a gas price (e.g., 50 Gwei)
    gas_price = w3.toWei('0.00111177', 'gwei')

    # Define the gas limit for a simple Ether transfer
    gas_limit = 21000

    # Get the sender's nonce
    w3.eth.default_account = Web3.toChecksumAddress(sender_address)
    nonce = w3.eth.get_transaction_count(sender_address)

    # Initialize total gas needed
    total_gas = 0

    # Collect transaction data for each recipient with a sequence number
    txs = []
    tx_sequence_number = 0
    for recipient_address, amount in recipients.items():
        recipient_address_checksum = Web3.toChecksumAddress(recipient_address)
        amount_in_wei = w3.toWei(amount, 'ether')
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
    total_cost = total_gas * gas_price + sum(w3.toWei(amount, 'ether') for amount in recipients.values())
    if sender_balance < total_cost:
        raise ValueError("Insufficient balance for transactions and gas fees.")

    # Sign and send transactions
    signed_txs = []
    for tx_sequence, tx in txs:
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        signed_txs.append((tx_sequence, signed_tx))

    for tx_sequence, signed_tx in signed_txs:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction {tx_sequence + 1}:")
        print(f"  Hash: {tx_hash.hex()}")
        print(f"  From: {sender_address}")
        print(f"  To: {list(recipients.keys())[tx_sequence]}")  # Changed recipients.keys() to list(recipients.keys())
        print(f"  Amount: {list(recipients.values())[tx_sequence]} ETH")
        print(f"  Gas Price: {w3.fromWei(gas_price, 'gwei')} Gwei")

        # Check transaction receipt and status
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print(f"Transaction Success!")
            print(f"  Block Number: {receipt.blockNumber}")
            print(f"  Gas Used: {receipt.gasUsed}")
        else:
            print(f"Transaction Failed!")

        # Print current balance after each transaction
        current_balance = check_balance(w3, sender_address)
        print(f"Current Balance: {current_balance} ETH\n")

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

    # Check sender's balance before sending
    initial_balance = check_balance(w3, sender_address)
    print(f"Initial Balance: {initial_balance} ETH")

    # Send Ether
    send_ether(w3, sender_address, private_key, recipients)

    # Check sender's balance after sending
    final_balance = check_balance(w3, sender_address)
    print(f"Final Balance: {final_balance} ETH")

    # Print a new line for separation
    print()
