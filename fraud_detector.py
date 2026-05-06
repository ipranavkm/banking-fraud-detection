"""
FraudDetector class for identifying suspicious bank transactions using z-score statistical anomaly detection.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from account import Account


class InsufficientDataError(Exception):
    # raised when there is not enough transaction history to perform analysis
    pass


class InvalidTransactionError(Exception):
    # raised when a transaction has invalid or missing fields
    pass


class FraudDetector:
    """
    Detects fraudulent transactions using z-score statistical analysis.

    Compares each incoming transaction amount against the account's historical transaction amounts.
    If z-score exceeds the configured threshold, the transaction is flagged

    Attributes:
    - threshold (float): Z-score threshold above which a transaction is flagged
    - min_history (int): Minimum number of past transactions required for analysis
    - flagged_transaction (List[Dict]): A list of dictionaries that store all flagged transactions
    """

    def __init__(self, threshold: float = 2.0, min_history: int = 3):
        '''
        Initialize the FraudDector

        Args:
        -threshold: Z-score cutoff for flagging (default 2.0).
        -min_history: Minimum transactions need before analysis (default 3)

        Raises:
        -ValueError: If threshold is not positive or min_history < 1
        '''

        if threshold <= 0:
            raise ValueError(f"Threshold must be positive, threshold = {threshold}")
        if min_history < 1:
            raise ValueError(f"min_history must be at least 1, got {min_history}")

        self.threshold = threshold
        self.min_history = min_history
        self.flagged_transactions: List[Dict[str, Any]] = []

    # ------------ Fraud Detection Methods ------------------

    def analyze_transaction(self, account: Account, amount: float) -> bool:
        """
        -Determines whether a single transaction amount is suspicious
        -Uses the account's existing transaction history as the baseline.
        -The transaction itself is NOT recorded on the account when this method is called

        Args:
        -account: The account object being analyzed.
        -amount: The proposed transaction amount.

        Returns:
        -bool: True if the transaction is flagged as suspicious

        Raises:
        -TypeError: If account is not an account instance.
        -InvalidTransactionError: If amount is not a positive number
        -InsufficientDataError: If account has fewer than min_history transactions
        """

        if not isinstance(account, Account):
            raise TypeError(f"Expected Account instance, got {type(account).__name__}")

        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InvalidTransactionError(f"Transaction must be a positive number, got {amount}")

        # Only use deposits as baseline — excludes initial deposit, withdrawals, and transfers
        history = [
            t["amount"] for t in account.transaction_history
            if t["type"] not in ("initial_deposit", "withdrawal", "transfer_out", "transfer_in")
        ]

        if len(history) < self.min_history:
            raise InsufficientDataError(f"Account {account.account_id} has only {len(history)} transaction(s); "
                                            f"need at least {self.min_history} for analysis.")

        mean = np.mean(history)
        std = np.std(history)

        # Avoid division by zero when all transactions are identical

        if std == 0:
            is_fraud = False
        else:
            z_score = abs((amount - mean) / std)
            if z_score > self.threshold:
                is_fraud = True
            else:
                is_fraud = False

        if is_fraud:
            self._record_flag(account, amount, float(mean), float(std))

        return is_fraud

    def analyze_account(self, account: Account) -> Dict[str, Any]:
        """
        Perform a full statistical summary of an account's transaction history.

        Args:
        -account: The Account object to analyze

        Returns:
        -Dict containing mean, std, min, max, transaction count, and any existing flagged amounts based on
        z score analysis of history.

        Raises:
        -TypeError: If account is not an Account instance.
        -InsufficientDataError: If not enough transaction history exists.
        """

        if not isinstance(account, Account):
            raise TypeError(f"Expected Account instance, got {type(account).__name__}")
 
        # Only use deposits as baseline — excludes initial deposit, withdrawals, and transfers
        history = [
            t["amount"] for t in account.transaction_history
            if t["type"] not in ("initial_deposit", "withdrawal", "transfer_out", "transfer_in")
        ]
 
        if len(history) < self.min_history:
            raise InsufficientDataError(
                f"Account {account.account_id} needs at least {self.min_history} "
                f"transactions for a full analysis."
            )
 
        mean = float(np.mean(history))
        std = float(np.std(history))
        flagged = []
 
        for amount in history:
            if std > 0:
                z = abs((amount - mean) / std)
                if z > self.threshold:
                    flagged.append(amount)
                    self._record_flag(account, amount, mean, std)
 
        return {
            "account_id": account.account_id,
            "owner": account.owner_name,
            "transaction_count": len(history),
            "mean": round(mean, 2),
            "std": round(std, 2),
            "min": round(float(np.min(history)), 2),
            "max": round(float(np.max(history)), 2),
            "flagged_amounts": flagged,
            "flagged_count": len(flagged),
        }

    def get_flagged_transactions(self) -> List[Dict[str, Any]]:
        """
        Return all transactions flagged during this session.

        Returns:
        -List of flagged transaction records.
        """
        return list(self.flagged_transactions)

    def clear_flags(self) -> None:
        """Reset the flagged transactions log."""
        self.flagged_transactions.clear()

    # -------------- Internal Helper Functions ------------------

    def _record_flag(self, account: Account, amount: float, mean: float, std: float) -> None:
        """
        Append a flagged transaction to the internal log.

        Args:
        -account: The account associated with the suspicious transaction.
        -amount: The flagged transaction amount.
        -mean: Historical mean at the time of detection.
        -std: Historical standard deviation at the time of detection.
        """
        z_score = abs((amount - mean) / std) if std > 0 else 0.0
        record = {
            "timestamp": datetime.now().isoformat(),
            "account_id": account.account_id,
            "owner": account.owner_name,
            "flagged_amount": amount,
            "historical_mean": round(mean, 2),
            "historical_std": round(std, 2),
            "z_score": round(z_score, 4),
            "threshold_used": self.threshold,
            }
        self.flagged_transactions.append(record)

        # ------------- Dunder Methods -------------

    def __str__(self) -> str:
        return (
            f"FraudDetector(threshold={self.threshold}, "
            f"min_history={self.min_history}, "
            f"flags_this_session={len(self.flagged_transactions)})")

    def __repr__(self) -> str:
        return (
            f"FraudDetector(threshold={self.threshold!r}, "
            f"min_history={self.min_history!r})")
