"""Visualization functions for transaction data."""

import matplotlib.pyplot as plt
from typing import List
from account import Account


def plot_transaction_amounts(account: Account) -> None:
    """
    Plot transaction amounts over time for a single account.
    
    Args:
        account: Account object to visualize
    """
    amounts = account.get_transaction_amounts()
    
    if not amounts:
        print(f"No transactions to plot for account {account.account_id}")
        return
    
    plt.figure(figsize=(10, 6))
    plt.plot(amounts, marker='o', linestyle='-', linewidth=2, markersize=6)
    plt.title(f"Transaction History - {account.owner_name} ({account.account_id})")
    plt.xlabel("Transaction Number")
    plt.ylabel("Amount ($)")
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
    plt.grid(True, alpha=0.3)
    plt.show()


def plot_balance_comparison(accounts: List[Account]) -> None:
    """
    Create bar chart comparing balances across accounts.
    
    Args:
        accounts: List of Account objects
    """
    if not accounts:
        print("No accounts to plot")
        return
    
    names = [f"{acc.owner_name}\n({acc.account_id})" for acc in accounts]
    balances = [acc.balance for acc in accounts]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, balances, color='skyblue', edgecolor='navy')
    
    for bar, balance in zip(bars, balances):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'${balance:.2f}', ha='center', va='bottom')
    
    plt.title("Account Balance Comparison")
    plt.ylabel("Balance ($)")
    plt.xticks(rotation=15)
    plt.grid(axis='y', alpha=0.3)
    plt.show()