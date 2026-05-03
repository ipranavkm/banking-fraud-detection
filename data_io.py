'''
CSV data I/O modules for the Banking Fraud Detection System.

Provides function to save and load transaction records and account summaries to/from CS files using pandas
'''

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from account import Account


# ------------ Custom Exceptions -----------------

class CSVReadError(Exception):
    """Raised when a CSV file cannot be read or parsed."""
    pass


class CSVWriteError(Exception):
    """Raised when data cannot be written to a CSV file."""
    pass


class EmptyDataError(Exception):
    """Raised when no data is available to save or process."""
    pass


# -------------- Transaction CSV I/O ---------------

def save_transactions_to_csv(transactions: List[Dict[str, Any]], filepath: str = "data/transactions.csv") -> str:
    """
    save a list of transaction dictionaries to a CSV file

    Args:
    trnasactions: List of transactions dicts (from transaction_simulator or Account.transaction_history entries).
    filepath: destination file path (default: data/transactions.csv).

    Returns:
    str: absolute path of the saved file

    raises:
    EmptyDataError: If the transaction list is empty
    CSVWriteError: If the file cannot be written
    TypeError: If transactions is not a list
    """

    if not isinstance(transactions, list):
        raise TypeError(f"Expected list of transactions, got {type(transactions).__name__}")

    if len(transactions) == 0:
        raise EmptyDataError("No transactions to save — list is empty.")

        # Validate each row has at minimum an 'amount' and 'account_id'
    for i, txn in enumerate(transactions):
        if not isinstance(txn, dict):
            raise TypeError(f"Transaction at index {i} must be a dict, got {type(txn).__name__}")
        if "amount" not in txn:
            raise ValueError(f"Transaction at index {i} is missing required field 'amount'.")
        if "account_id" not in txn:
            raise ValueError(f"Transaction at index {i} is missing required field 'account_id'.")

    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        df = pd.DataFrame(transactions)

        # Ensure timestamp column exists
        if "timestamp" not in df.columns:
            df["timestamp"] = datetime.now().isoformat()

        df.to_csv(filepath, index=False)
        return os.path.abspath(filepath)

    except PermissionError as e:
        raise CSVWriteError(
            f"Permission denied writing to '{filepath}': {e}"
        ) from e
    except OSError as e:
        raise CSVWriteError(
            f"OS error writing to '{filepath}': {e}"
        ) from e


def load_transactions_from_csv(filepath: str) -> List[Dict[str, Any]]:
    """
    Load transaction records from a CSV file.

    Args:
    filepath: Path to the CSV file.

    Returns:
    List of transaction dictionaries.

    Raises:
    FileNotFoundError: If the file does not exist.
    CSVReadError: If the file cannot be parsed as CSV.
    EmptyDataError: If the CSV file is empty or has no data rows.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Transaction file not found: '{filepath}'")

    if os.path.getsize(filepath) == 0:
        raise EmptyDataError(f"CSV file is empty: '{filepath}'")

    try:
        df = pd.read_csv(filepath)
    except pd.errors.EmptyDataError:
        raise EmptyDataError(f"No data rows found in '{filepath}'.")
    except pd.errors.ParserError as e:
        raise CSVReadError(f"Failed to parse CSV '{filepath}': {e}") from e
    except OSError as e:
        raise CSVReadError(f"Cannot read file '{filepath}': {e}") from e

    if df.empty:
        raise EmptyDataError(f"CSV loaded but contains no rows: '{filepath}'")

    # Validate expected columns
    required_cols = {"account_id", "amount"}
    missing = required_cols - set(df.columns)
    if missing:
        raise CSVReadError(
            f"CSV '{filepath}' is missing required column(s): {missing}"
        )

    # Convert amount column to float, coercing bad values
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    invalid_rows = df["amount"].isna().sum()
    if invalid_rows > 0:
        print(f"Warning: {invalid_rows} row(s) had non-numeric 'amount' values and were dropped.")
        df = df.dropna(subset=["amount"])

    return df.to_dict(orient="records")

# ---------- Account Summary CSV I/O --------------------
def save_accounts_to_csv(accounts: List[Account],
                         filepath: str = "data/accounts.csv") -> str:
    """
    Save a summary of Account objects to a CSV file.

    Saves account_id, owner_name, balance, and transaction count.

    Args:
    accounts: List of Account objects.
    filepath: Destination file path (default: data/accounts.csv).

    Returns:
    str: Absolute path of the saved file.

    Raises:
    -EmptyDataError: If the accounts list is empty.
    -TypeError: If any item in the list is not an Account.
    -CSVWriteError: If the file cannot be written.
    """
    if not isinstance(accounts, list):
        raise TypeError(f"Expected list of Accounts, got {type(accounts).__name__}")

    if len(accounts) == 0:
        raise EmptyDataError("No accounts to save — list is empty.")

    rows = []
    for i, acc in enumerate(accounts):
        # Import here to avoid circular import issues if needed
        from account import Account as _Account
        if not isinstance(acc, _Account):
            raise TypeError(
                f"Item at index {i} must be an Account instance, got {type(acc).__name__}"
            )
        rows.append({
            "account_id": acc.account_id,
            "owner_name": acc.owner_name,
            "balance": round(acc.balance, 2),
            "transaction_count": len(acc.transaction_history),
            "snapshot_timestamp": datetime.now().isoformat(),
        })

    try:
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
        return os.path.abspath(filepath)

    except PermissionError as e:
        raise CSVWriteError(f"Permission denied writing to '{filepath}': {e}") from e
    except OSError as e:
        raise CSVWriteError(f"OS error writing to '{filepath}': {e}") from e


def load_accounts_from_csv(filepath: str) -> pd.DataFrame:
    """
    -Load account summary data from a CSV file as a DataFrame.

    -Note: This returns a DataFrame, not Account objects, since balances and history cannot be fully
    reconstructed from a summary CSV.
    -Use this for reporting and analysis purposes.

    Args:
    -filepath: Path to the accounts CSV file.

    Returns:
    -pd.DataFrame with account summary columns.

    Raises:
    -FileNotFoundError: If the file does not exist.
    -CSVReadError: If parsing fails.
    -EmptyDataError: If the file is empty.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Accounts file not found: '{filepath}'")

    if os.path.getsize(filepath) == 0:
        raise EmptyDataError(f"CSV file is empty: '{filepath}'")

    try:
        df = pd.read_csv(filepath)
    except pd.errors.EmptyDataError:
        raise EmptyDataError(f"No data rows found in '{filepath}'.")
    except pd.errors.ParserError as e:
        raise CSVReadError(f"Failed to parse CSV '{filepath}': {e}") from e
    except OSError as e:
        raise CSVReadError(f"Cannot read file '{filepath}': {e}") from e

    if df.empty:
        raise EmptyDataError(f"CSV loaded but contains no rows: '{filepath}'")

    required_cols = {"account_id", "owner_name", "balance"}
    missing = required_cols - set(df.columns)
    if missing:
        raise CSVReadError(
            f"Accounts CSV '{filepath}' is missing required column(s): {missing}"
        )

    df["balance"] = pd.to_numeric(df["balance"], errors="coerce")
    return df
