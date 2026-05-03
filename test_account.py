from account import Account

print("=" * 40)
print("TESTING ACCOUNT CLASS")
print("=" * 40)

# Create account
acc1 = Account("T001", "Test User 1", 1000)
acc2 = Account("T002", "Test User 2", 500)

print("\n--- Test __str__ ---")
print(acc1)
print(acc2)

print("\n--- Test deposit ---")
acc1.deposit(500)
print(f"After deposit $500: ${acc1.balance}")

print("\n--- Test withdraw ---")
acc1.withdraw(200)
print(f"After withdraw $200: ${acc1.balance}")

print("\n--- Test transfer ---")
acc1.transfer(300, acc2)
print(f"After transfer $300:")
print(f"  Account 1: ${acc1.balance}")
print(f"  Account 2: ${acc2.balance}")

print("\n--- Test __add__ operator ---")
total = acc1 + acc2
print(f"Combined balance: ${total}")

print("\n--- Test transaction history ---")
print(f"Transaction amounts: {acc1.get_transaction_amounts()}")

print("\n✅ All Account tests passed!")
