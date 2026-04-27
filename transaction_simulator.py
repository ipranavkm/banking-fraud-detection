"""Transaction simulator with generator function for streaming transactions."""

import random
import time
from typing import Generator, Dict, Any
from datetime import datetime


def simulate_transaction_stream(account_ids: list, 
                                num_transactions: int = 10,
                                delay_seconds: float = 0.1) -> Generator[Dict[str, Any], None, None]:
    """
    Generator function that simulates a live transaction stream.
    
    Args:
        account_ids: List of valid account IDs
        num_transactions: Number of transactions to generate
        delay_seconds: Delay between transaction generations
        
    Yields:
        Dict: Transaction dictionary with amount, account_id, timestamp
    """
    transaction_types = ["deposit", "withdrawal", "transfer"]
    
    for i in range(num_transactions):
        time.sleep(delay_seconds)
        
        transaction = {
            "transaction_id": i + 1,
            "timestamp": datetime.now().isoformat(),
            "account_id": random.choice(account_ids),
            "type": random.choice(transaction_types),
            "amount": round(random.uniform(10.0, 1000.0), 2)
        }
        
        yield transaction


def generate_sample_transactions(num_transactions: int = 20) -> list:
    """
    Generate a list of sample transactions for testing.
    
    Args:
        num_transactions: Number of transactions to generate
        
    Returns:
        list: List of transaction dictionaries
    """
    account_ids = ["A001", "A002", "A003"]
    
    # List comprehension to generate transactions
    transactions = [
        {
            "account_id": random.choice(account_ids),
            "amount": random.uniform(5.0, 5000.0),
            "type": random.choice(["deposit", "withdrawal"])
        }
        for _ in range(num_transactions)
    ]
    
    return transactions