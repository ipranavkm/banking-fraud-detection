from account import Account
from visualizer import plot_transaction_amounts, plot_balance_comparison

print("=" * 40)
print("TESTING VISUALIZER")
print("=" * 40)

# Create test account with transactions
acc = Account("V001", "Visual Test", 1000)
acc.deposit(200)
acc.deposit(300)
acc.withdraw(100)
acc.deposit(500)
acc.withdraw(50)

print("\n--- Transaction history ---")
print(f"Amounts: {acc.get_transaction_amounts()}")

print("\n--- Showing graph 1: Transaction history ---")
plot_transaction_amounts(acc)

print("\n--- Showing graph 2: Balance comparison ---")
plot_balance_comparison([acc])

print("\n✅ Visualizer test passed! (Close graph windows to continue)")
