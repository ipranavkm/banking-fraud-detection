# Banking Fraud Detection System

## Team Members
- [Pranav Itikarlapalli], [pitikarl@stevens.edu]
- [Ishaan Bhalodia], [ishaanbhalodia10@gmail.com]

## Project Description
This project simulates a banking transaction system with automated fraud detection. The system maintains account balances, records transaction histories, and detects suspicious activity using statistical anomaly detection (z-score analysis). Transactions that deviate significantly from a customer's normal behavior are flagged as potential fraud.

### Problem Solved
Banks process millions of transactions daily. Manual fraud detection is impossible. This system automatically identifies unusual transaction patterns that may indicate stolen credentials, account takeover, or money laundering.

### Dependencies
- Python 3.12+
- numpy - Statistical calculations
- pandas - CSV data handling
- matplotlib - Data visualization
- pytest - Unit testing

### File Structure
banking-fraud-detection/
├── README.md
├── requirements.txt
├── main.ipynb
├── account.py
├── fraud_detector.py
├── data_io.py
├── transaction_simulator.py
├── visualizer.py
├── test_account.py
├── test_fraud_detector.py
└── data/
└── accounts.csv

## How to Run the Program

### 1. Install dependencies
```bash
pip install -r requirements.txt

pytest -v

jupyter notebook main.ipynb

Main Contributions
Pranav Itikarlapalli

    Repository setup and project structure

    Account class with deposit/withdraw/transfer

    Operator overloading (add) and str

    Transaction generator function

    Visualization module

Ishaan Bhalodia

    FraudDetector class with statistical analysis

    CSV data I/O with exception handling

    Pytest test cases

    Main Jupyter notebook integration

    Documentation