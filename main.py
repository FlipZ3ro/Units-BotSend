import os
from web3 import Web3
import time
from dotenv import load_dotenv
import random
from colorama import Fore, Style  # Import untuk warna teks

# Print header with colors
print(Fore.GREEN + "+-----------------------------------------+")
print(Fore.GREEN + "               Units-Bot-Send")
print(Fore.GREEN + "          Modif from HappyCuanAirdrop")
print(Fore.GREEN + "                    arapzz")
print(Fore.GREEN + "+-----------------------------------------+")

# Load environment variables from .env file
load_dotenv()

# Initialize Web3 and other configurations
rpc_url = os.getenv("RPC_URL")  # Pastikan ini sesuai dengan alamat server RPC Anda
w3 = Web3(Web3.HTTPProvider(rpc_url))

def get_balance(w3, address):
    # Get balance in Ether
    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    return balance_eth

def send_ether(w3, private_key, recipients):
    # Disable automatic gas price checking
    w3.middleware_onion.clear()

    # Define initial gas price (e.g., 1 Gwei)
    gas_price = w3.to_wei('0.00111177', 'gwei')

    # Define the gas limit for a simple Ether transfer
    gas_limit = 60000

    # Get the sender's address from private key
    sender_address = w3.eth.account.from_key(private_key).address
    print(f"Address : {sender_address}")

    # Get sender's Ethereum balance
    initial_balance_eth = get_balance(w3, sender_address)
    print(f"Balance : {initial_balance_eth} UNIT0")

    # Get the sender's nonce
    nonce = w3.eth.get_transaction_count(sender_address)

    # Initialize total gas needed
    total_gas = 0

    # Collect transaction data for each recipient with a sequence number
    txs = []
    tx_sequence_number = 1
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
    if sender_balance < total_cost:
        raise ValueError("Insufficient balance for transactions and gas fees.")

    # Sign and send transactions
    signed_txs = []
    for tx_sequence, tx in txs:
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        signed_txs.append((tx_sequence, signed_tx))

    for tx_sequence, signed_tx in signed_txs:
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"{Fore.GREEN}Transaction {tx_sequence} successfully sent. Transaction hash: {tx_hash.hex()}{Style.RESET_ALL}")
            nonce = w3.eth.get_transaction_count(sender_address)  # Update nonce after each successful transaction
        except ValueError as e:
            error_message = str(e)
            print(f"{Fore.RED}Error sending transaction {tx_sequence}: {error_message}{Style.RESET_ALL}")

# Contoh penggunaan fungsi send_ether
private_key = os.getenv("PRIVATE_KEY")  # Ganti dengan cara yang sesuai untuk mendapatkan private key dari .env
num_transactions = int(input("Enter the number of transactions you want to send: "))

# Countdown before proceeding
for i in range(1, 10):
    print(f"{Fore.BLUE}\rStarting in {i} seconds...", end='', flush=True)
    time.sleep(1)
print(f"{Fore.YELLOW}\rStarting now!           {Style.RESET_ALL}")

# Generate random recipient addresses dan jumlah Ether yang akan dikirim ke masing-masing (dalam Ether)
recipients = {}
for i in range(num_transactions):
    new_account = w3.eth.account.create()
    recipient_address = new_account.address
    amount = round(random.uniform(0.00000001, 0.00000001), 8)  # Jumlah acak antara 0.00001 dan 0.0001 Ether
    recipients[recipient_address] = amount

send_ether(w3, private_key, recipients)
