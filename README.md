# Banking Fraud Detection System

## Team Members
| Name | Email |
|---|---|
| Pranav Itikarlapalli | pitikarl@stevens.edu |20038694
| Ishaan Bhalodia | ishaanbhalodia10@gmail.com |20040591

---

## Project Description
This project simulates a banking transaction system with automated fraud detection. The system maintains account balances, records transaction histories, and detects suspicious activity using statistical anomaly detection (z-score analysis). Transactions that deviate significantly from a customer's normal behavior are flagged as potential fraud.

### Problem Solved
Banks process millions of transactions daily. Manual fraud detection is impossible at scale. This system automatically identifies unusual transaction patterns that may indicate stolen credentials, account takeover, or money laundering — without requiring any labeled training data.

---

## How It Works

The `FraudDetector` class uses **z-score analysis** to compare each incoming transaction against an account's deposit history:

```
z = | ( transaction_amount − mean_of_history ) / std_of_history |
```

If `z > threshold` (default: **2.0**), the transaction is flagged as suspicious. Only pure deposit transactions are used as the baseline — initial deposits, withdrawals, and transfers are excluded to avoid skewing the mean.

---

## Dependencies
- Python 3.12+
- numpy — Statistical calculations (z-score analysis)
- pandas — CSV data handling
- matplotlib — Data visualization
- pytest — Unit testing

Install all dependencies with:
```bash
pip install -r requirements.txt
```

---

## File Structure

```
banking-fraud-detection/
-README.md
-requirements.txt
- main.ipynb
- account.py
- fraud_detector.py
- data_io.py
- transaction_simulator.py
- visualizer.py
- test_account.py
- test_fraud_detector.py
- data/
    - accounts.csv
    - transactions.csv
    
```

### Module Descriptions

| File                       | Description                                                             |
|----------------------------|-------------------------------------------------------------------------|
| `account.py`               | `Account` class — deposits, withdrawals, transfers, transaction history |
| `fraud_detector.py`        | `FraudDetector` class — z-score detection, flagging, session logging    |
| `data_io.py`               | CSV save/load functions for transactions and account summaries          |
| `transaction_simulator.py` | Generator-based live transaction stream simulator                       |
| `visualizer.py`            | Matplotlib plots for transaction history and balance comparison         |
| `test_fraud_detector.py`   | Pytest test suite for `FraudDetector` and `data_io`                     |
| `test_account.py`          | Pytest test suite for `Account` class                                   |
| `test_my_generator.py`        | Pytest test suite for `Transaction Simulator` class                       |
| `test_my_visualizer.py`       | Pytest test suite for 'Visualizer' class                                |
  
---

## How to Run

### Run the main program
```bash
jupyter notebook main.ipynb
```

### Run the test suite
```bash
pytest test_fraud_detector.py -v
pytest test_account.py -v
pytest test_my_visualizer -v 
pytest test_my_generator -v
```

---

## Usage Examples

### Creating accounts and recording transactions
```python
from account import Account

alice = Account("A001", "Alice Smith", 1000.0)
alice.deposit(100.0)
alice.withdraw(50.0)
alice.transfer(25.0, bob)
```

### Running fraud detection
```python
from fraud_detector import FraudDetector

detector = FraudDetector(threshold=2.0, min_history=3)

# Check a single incoming transaction
is_fraud = detector.analyze_transaction(alice, 9999.0)
print(is_fraud)  # True — flagged

# Full analysis of account history
summary = detector.analyze_account(alice)
print(summary)

# View all flagged transactions this session
flags = detector.get_flagged_transactions()
```

### Saving and loading CSV data
```python
from data_io import save_transactions_to_csv, load_transactions_from_csv

save_transactions_to_csv(transactions, "data/transactions.csv")
loaded = load_transactions_from_csv("data/transactions.csv")
```

---

## Exception Handling

| Exception | Module | Trigger |
|---|---|---|
| `InsufficientDataError` | `fraud_detector` | Account has fewer transactions than `min_history` |
| `InvalidTransactionError` | `fraud_detector` | Amount is zero, negative, or non-numeric |
| `EmptyDataError` | `data_io` | Saving empty list or loading empty CSV |
| `CSVReadError` | `data_io` | File cannot be parsed or missing required columns |
| `CSVWriteError` | `data_io` | File cannot be written due to OS or permission error |
| `FileNotFoundError` | `data_io` | Specified CSV file does not exist |
| `ValueError` | `account`, `fraud_detector` | Invalid numeric inputs (e.g. negative balance) |
| `TypeError` | `fraud_detector`, `data_io` | Wrong type passed to a function |

---

## Main Contributions

### Pranav Itikarlapalli
- Repository setup and project structure
- `Account` class with deposit, withdraw, and transfer
- Operator overloading (`__add__`, `__str__`, `__repr__`)
- Transaction simulation generator
- Visualization module
- Added unit tests for Account, Generator and Visualizer 

### Ishaan Bhalodia
- `FraudDetector` class with z-score statistical analysis
- CSV data I/O (`data_io.py`) with full exception handling
- Pytest test suite (`test_fraud_detector.py`)
- Main program (`main.ipynb`)
- Documentation and README
