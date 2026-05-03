"""
Pytest test suite for FraudDetector and data_io modules.

Run with:
pytest test_fraud_detector.py -v
"""

import os
import pytest
import pandas as pd

from account import Account
from fraud_detector import FraudDetector, InsufficientDataError, InvalidTransactionError
from data_io import (
    save_transactions_to_csv,
    load_transactions_from_csv,
    save_accounts_to_csv,
    load_accounts_from_csv,
    CSVReadError,
    CSVWriteError,
    EmptyDataError,
)




# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def basic_account():
    """Account with a few normal transactions (~$100 range)."""
    acc = Account("A001", "Alice Smith", 100.0)
    acc.deposit(80.0)
    acc.deposit(120.0)
    acc.deposit(100.0)
    acc.deposit(90.0)
    acc.deposit(110.0)
    return acc


@pytest.fixture
def detector():
    """Default FraudDetector with threshold=2.0."""
    return FraudDetector(threshold=2.0, min_history=3)


@pytest.fixture
def sample_transactions():
    """List of valid transaction dicts."""
    return [
        {"account_id": "A001", "amount": 100.0, "type": "deposit", "timestamp": "2026-01-01T10:00:00"},
        {"account_id": "A001", "amount": 200.0, "type": "withdrawal", "timestamp": "2026-01-02T11:00:00"},
        {"account_id": "A002", "amount": 50.0, "type": "deposit", "timestamp": "2026-01-03T12:00:00"},
    ]


@pytest.fixture
def tmp_csv(tmp_path):
    """Provide a temporary file path for CSV tests."""
    return str(tmp_path / "test_transactions.csv")


@pytest.fixture
def tmp_accounts_csv(tmp_path):
    """Provide a temporary file path for accounts CSV tests."""
    return str(tmp_path / "test_accounts.csv")


# ===========================================================================
# FraudDetector — initialization
# ===========================================================================

class TestFraudDetectorInit:

    def test_default_threshold(self):
        fd = FraudDetector()
        assert fd.threshold == 2.0

    def test_custom_threshold(self):
        fd = FraudDetector(threshold=3.5)
        assert fd.threshold == 3.5

    def test_custom_min_history(self):
        fd = FraudDetector(min_history=5)
        assert fd.min_history == 5

    def test_invalid_threshold_zero(self):
        with pytest.raises(ValueError):
            FraudDetector(threshold=0)

    def test_invalid_threshold_negative(self):
        with pytest.raises(ValueError):
            FraudDetector(threshold=-1.0)

    def test_invalid_min_history(self):
        with pytest.raises(ValueError):
            FraudDetector(min_history=0)

    def test_str_representation(self):
        fd = FraudDetector(threshold=2.0)
        assert "FraudDetector" in str(fd)
        assert "2.0" in str(fd)


# ===========================================================================
# FraudDetector — analyze_transaction
# ===========================================================================

class TestAnalyzeTransaction:

    def test_normal_transaction_not_flagged(self, detector, basic_account):
        """A transaction close to the mean should not be flagged."""
        result = detector.analyze_transaction(basic_account, 105.0)
        assert result is False

    def test_large_transaction_flagged(self, detector, basic_account):
        """A very large outlier should be flagged."""
        result = detector.analyze_transaction(basic_account, 9999.0)
        assert result is True

    def test_flagged_transaction_recorded(self, detector, basic_account):
        """Flagged transaction should appear in flagged_transactions list."""
        detector.analyze_transaction(basic_account, 9999.0)
        flags = detector.get_flagged_transactions()
        assert len(flags) == 1
        assert flags[0]["account_id"] == "A001"
        assert flags[0]["flagged_amount"] == 9999.0

    def test_normal_transaction_not_recorded(self, detector, basic_account):
        """Normal transaction should not be added to flagged list."""
        detector.analyze_transaction(basic_account, 100.0)
        assert len(detector.get_flagged_transactions()) == 0

    def test_insufficient_history_raises(self, detector):
        """Account with fewer transactions than min_history should raise."""
        acc = Account("A002", "Bob", 500.0)
        acc.deposit(50.0)  # only 2 transactions total (initial + deposit)
        with pytest.raises(InsufficientDataError):
            detector.analyze_transaction(acc, 100.0)

    def test_invalid_amount_zero(self, detector, basic_account):
        with pytest.raises(InvalidTransactionError):
            detector.analyze_transaction(basic_account, 0)

    def test_invalid_amount_negative(self, detector, basic_account):
        with pytest.raises(InvalidTransactionError):
            detector.analyze_transaction(basic_account, -50.0)

    def test_invalid_amount_string(self, detector, basic_account):
        with pytest.raises(InvalidTransactionError):
            detector.analyze_transaction(basic_account, "large")

    def test_invalid_account_type(self, detector):
        with pytest.raises(TypeError):
            detector.analyze_transaction("not_an_account", 100.0)

    def test_returns_bool(self, detector, basic_account):
        result = detector.analyze_transaction(basic_account, 100.0)
        assert isinstance(result, bool)

    def test_multiple_flags_accumulate(self, detector, basic_account):
        detector.analyze_transaction(basic_account, 9999.0)
        detector.analyze_transaction(basic_account, 8888.0)
        assert len(detector.get_flagged_transactions()) == 2


# ===========================================================================
# FraudDetector — analyze_account
# ===========================================================================

class TestAnalyzeAccount:

    def test_returns_dict(self, detector, basic_account):
        result = detector.analyze_account(basic_account)
        assert isinstance(result, dict)

    def test_result_keys(self, detector, basic_account):
        result = detector.analyze_account(basic_account)
        expected_keys = {"account_id", "owner", "transaction_count", "mean", "std", "min", "max",
                         "flagged_amounts", "flagged_count"}
        assert expected_keys.issubset(result.keys())

    def test_correct_account_id(self, detector, basic_account):
        result = detector.analyze_account(basic_account)
        assert result["account_id"] == "A001"

    def test_no_flags_for_normal_account(self, detector, basic_account):
        result = detector.analyze_account(basic_account)
        assert result["flagged_count"] == 0

    def test_insufficient_history_raises(self, detector):
        acc = Account("A003", "Carol", 200.0)
        with pytest.raises(InsufficientDataError):
            detector.analyze_account(acc)

    def test_invalid_account_type(self, detector):
        with pytest.raises(TypeError):
            detector.analyze_account({"account_id": "X"})


# ===========================================================================
# FraudDetector — clear_flags
# ===========================================================================

class TestClearFlags:

    def test_clear_flags(self, detector, basic_account):
        detector.analyze_transaction(basic_account, 9999.0)
        assert len(detector.get_flagged_transactions()) == 1
        detector.clear_flags()
        assert len(detector.get_flagged_transactions()) == 0


# ------------------ data_io — save_transactions_to_csv ------------------------


class TestSaveTransactionsToCSV:

    def test_creates_file(self, sample_transactions, tmp_csv):
        save_transactions_to_csv(sample_transactions, tmp_csv)
        assert os.path.exists(tmp_csv)

    def test_csv_has_correct_rows(self, sample_transactions, tmp_csv):
        save_transactions_to_csv(sample_transactions, tmp_csv)
        df = pd.read_csv(tmp_csv)
        assert len(df) == 3

    def test_csv_has_amount_column(self, sample_transactions, tmp_csv):
        save_transactions_to_csv(sample_transactions, tmp_csv)
        df = pd.read_csv(tmp_csv)
        assert "amount" in df.columns

    def test_empty_list_raises(self, tmp_csv):
        with pytest.raises(EmptyDataError):
            save_transactions_to_csv([], tmp_csv)

    def test_non_list_raises(self, tmp_csv):
        with pytest.raises(TypeError):
            save_transactions_to_csv("not a list", tmp_csv)

    def test_missing_amount_field_raises(self, tmp_csv):
        bad_data = [{"account_id": "A001", "type": "deposit"}]
        with pytest.raises(ValueError):
            save_transactions_to_csv(bad_data, tmp_csv)

    def test_missing_account_id_raises(self, tmp_csv):
        bad_data = [{"amount": 100.0, "type": "deposit"}]
        with pytest.raises(ValueError):
            save_transactions_to_csv(bad_data, tmp_csv)

    def test_returns_filepath_string(self, sample_transactions, tmp_csv):
        result = save_transactions_to_csv(sample_transactions, tmp_csv)
        assert isinstance(result, str)


# ---------------------- data_io — load_transactions_from_csv ------------------------

class TestLoadTransactionsFromCSV:

    def test_loads_correct_count(self, sample_transactions, tmp_csv):
        save_transactions_to_csv(sample_transactions, tmp_csv)
        loaded = load_transactions_from_csv(tmp_csv)
        assert len(loaded) == 3

    def test_loaded_records_are_dicts(self, sample_transactions, tmp_csv):
        save_transactions_to_csv(sample_transactions, tmp_csv)
        loaded = load_transactions_from_csv(tmp_csv)
        assert all(isinstance(r, dict) for r in loaded)

    def test_amount_is_float(self, sample_transactions, tmp_csv):
        save_transactions_to_csv(sample_transactions, tmp_csv)
        loaded = load_transactions_from_csv(tmp_csv)
        assert all(isinstance(r["amount"], float) for r in loaded)

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            load_transactions_from_csv("nonexistent_file.csv")

    def test_empty_file_raises(self, tmp_path):
        empty = str(tmp_path / "empty.csv")
        open(empty, "w").close()
        with pytest.raises(EmptyDataError):
            load_transactions_from_csv(empty)

    def test_missing_required_column_raises(self, tmp_path):
        bad_csv = str(tmp_path / "bad.csv")
        pd.DataFrame([{"type": "deposit"}]).to_csv(bad_csv, index=False)
        with pytest.raises(CSVReadError):
            load_transactions_from_csv(bad_csv)


# ----------------- data_io — save_accounts_to_csv / load_accounts_from_csv -------------------------

class TestAccountsCSV:

    def test_save_creates_file(self, tmp_accounts_csv):
        acc = Account("A001", "Alice", 500.0)
        save_accounts_to_csv([acc], tmp_accounts_csv)
        assert os.path.exists(tmp_accounts_csv)

    def test_save_correct_columns(self, tmp_accounts_csv):
        acc = Account("A001", "Alice", 500.0)
        save_accounts_to_csv([acc], tmp_accounts_csv)
        df = pd.read_csv(tmp_accounts_csv)
        assert "account_id" in df.columns
        assert "balance" in df.columns

    def test_save_empty_raises(self, tmp_accounts_csv):
        with pytest.raises(EmptyDataError):
            save_accounts_to_csv([], tmp_accounts_csv)

    def test_save_non_account_raises(self, tmp_accounts_csv):
        with pytest.raises(TypeError):
            save_accounts_to_csv([{"account_id": "X"}], tmp_accounts_csv)

    def test_load_returns_dataframe(self, tmp_accounts_csv):
        acc = Account("A001", "Alice", 500.0)
        save_accounts_to_csv([acc], tmp_accounts_csv)
        df = load_accounts_from_csv(tmp_accounts_csv)
        assert isinstance(df, pd.DataFrame)

    def test_load_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            load_accounts_from_csv("no_such_file.csv")

    def test_roundtrip_balance(self, tmp_accounts_csv):
        acc = Account("A001", "Alice", 750.0)
        save_accounts_to_csv([acc], tmp_accounts_csv)
        df = load_accounts_from_csv(tmp_accounts_csv)
        assert df.iloc[0]["balance"] == pytest.approx(750.0)

