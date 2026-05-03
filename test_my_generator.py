from transaction_simulator import simulate_transaction_stream, generate_sample_transactions

print("=" * 40)
print("TESTING TRANSACTION GENERATOR")
print("=" * 40)

print("\n--- Test generate_sample_transactions ---")
samples = generate_sample_transactions(5)
for i, t in enumerate(samples):
    print(f"  {i+1}. Account {t['account_id']}: ${t['amount']} ({t['type']})")

print("\n--- Test simulate_transaction_stream (generator) ---")
account_ids = ["A001", "A002", "A003"]
for transaction in simulate_transaction_stream(account_ids, num_transactions=3, delay_seconds=0.1):
    print(f"  Transaction #{transaction['transaction_id']}: "
          f"Account {transaction['account_id']} - "
          f"${transaction['amount']} ({transaction['type']})")

print("\n✅ All Generator tests passed!")
