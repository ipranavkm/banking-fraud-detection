"""Account class for managing bank account operations."""

from typing import List, Dict, Any
from datetime import datetime


class Account:
    """
    Bank account class managing deposits, withdrawals, transfers, and transaction history.
    
    Attributes:
        account_id (str): Unique account identifier
        owner_name (str): Name of account owner
        balance (float): Current account balance
        transaction_history (List[Dict]): List of transaction records
    """
    
    def __init__(self, account_id: str, owner_name: str, initial_balance: float = 0.0):
        """
        Initialize a new bank account.
        
        Args:
            account_id: Unique identifier for the account
            owner_name: Name of the account owner
            initial_balance: Starting balance (default 0.0)
        """
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self.account_id = account_id
        self.owner_name = owner_name
        self.balance = initial_balance
        self.transaction_history: List[Dict[str, Any]] = []
        
        # Record initial deposit if any
        if initial_balance > 0:
            self._add_transaction("initial_deposit", initial_balance)
    
    def _add_transaction(self, transaction_type: str, amount: float, 
                         to_account: str = None) -> None:
        """
        Add a transaction to the history.
        
        Args:
            transaction_type: Type of transaction (deposit, withdrawal, transfer)
            amount: Transaction amount
            to_account: Destination account ID (for transfers)
        """
        transaction = {
            "timestamp": datetime.now().isoformat(),
            "type": transaction_type,
            "amount": amount,
            "balance_after": self.balance,
            "to_account": to_account
        }
        self.transaction_history.append(transaction)
    
    def deposit(self, amount: float) -> bool:
        """
        Deposit money into the account.
        
        Args:
            amount: Amount to deposit (must be positive)
            
        Returns:
            bool: True if deposit successful
            
        Raises:
            ValueError: If amount is negative or zero
        """
        if amount <= 0:
            raise ValueError(f"Deposit amount must be positive, got {amount}")
        self.balance += amount
        self._add_transaction("deposit", amount)
        return True
    
    def withdraw(self, amount: float) -> bool:
        """
        Withdraw money from the account.
        
        Args:
            amount: Amount to withdraw (must be positive and ≤ balance)
            
        Returns:
            bool: True if withdrawal successful
            
        Raises:
            ValueError: If amount is negative/zero or exceeds balance
        """
        if amount <= 0:
            raise ValueError(f"Withdrawal amount must be positive, got {amount}")
        if amount > self.balance:
            raise ValueError(f"Insufficient funds. Balance: {self.balance}, Withdrawal: {amount}")
        self.balance -= amount
        self._add_transaction("withdrawal", amount)
        return True
    
    def transfer(self, amount: float, target_account: 'Account') -> bool:
        """
        Transfer money to another account.
        
        Args:
            amount: Amount to transfer
            target_account: Destination Account object
            
        Returns:
            bool: True if transfer successful
        """
        if amount <= 0:
            raise ValueError(f"Transfer amount must be positive, got {amount}")
        if amount > self.balance:
            raise ValueError(f"Insufficient funds for transfer. Balance: {self.balance}")
        
        # Perform transfer
        self.balance -= amount
        target_account.balance += amount
        
        # Record transactions
        self._add_transaction("transfer_out", amount, target_account.account_id)
        target_account._add_transaction("transfer_in", amount, self.account_id)
        
        return True
    
    def get_transaction_amounts(self) -> List[float]:
        """
        Extract all transaction amounts from history.
        
        Returns:
            List[float]: List of transaction amounts (positive for deposits, negative for withdrawals/transfers)
        """
        amounts = []
        for trans in self.transaction_history:
            if trans["type"] == "deposit" or trans["type"] == "initial_deposit":
                amounts.append(trans["amount"])
            elif trans["type"] == "withdrawal" or trans["type"] == "transfer_out":
                amounts.append(-trans["amount"])
        return amounts
    
    def __str__(self) -> str:
        """Return readable string representation of the account."""
        return f"Account({self.account_id}): {self.owner_name} | Balance: ${self.balance:.2f} | Transactions: {len(self.transaction_history)}"
    
    def __add__(self, other: 'Account') -> float:
        """
        Operator overload for +: returns combined balance of two accounts.
        
        Args:
            other: Another Account object
            
        Returns:
            float: Sum of both account balances
        """
        if not isinstance(other, Account):
            return NotImplemented
        return self.balance + other.balance
    
    def __repr__(self) -> str:
        """Return developer-friendly string representation."""
        return f"Account('{self.account_id}', '{self.owner_name}', {self.balance})"
