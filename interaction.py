from web3 import Web3

def send_ether(w3, sender_address, private_key, recipients):
    # Disable automatic gas price checking
    w3.middleware_onion.clear()

    # Define a gas price (e.g., 50 Gwei)
    gas_price = w3.to_wei('0.001000001', 'gwei')

    # Define the gas limit for a simple Ether transfer
    gas_limit = 21000

    # Get the sender's nonce
    w3.eth.default_account = Web3.to_checksum_address(sender_address)
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
    if sender_balance < total_cost:
        raise ValueError("Insufficient balance for transactions and gas fees.")

    # Sign and send transactions
    signed_txs = []
    for tx_sequence, tx in txs:
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        signed_txs.append((tx_sequence, signed_tx))

    for tx_sequence, signed_tx in signed_txs:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction {tx_sequence} successfully sent. Transaction hash: {tx_hash.hex()}")
