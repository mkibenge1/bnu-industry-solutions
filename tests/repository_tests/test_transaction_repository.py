import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

from models.bnu_models import ExpenseTransaction, SaleTransaction
from repositories.transaction_repository import TransactionRepository


class TestTransactionRepository(unittest.TestCase):
# test for save and load transactions
    def test_save_and_load_transactions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "transactions.json"
            repository = TransactionRepository(str(path))

            sale = SaleTransaction(
                transaction_id="T001",
                amount=100.0,
                created_at=datetime.now(),
                description="Sale",
                related_order_id="CO001",
            )
            expense = ExpenseTransaction(
                transaction_id="T002",
                amount=40.0,
                created_at=datetime.now(),
                description="Expense",
                related_order_id="PO001",
            )

            repository.save([sale, expense])
            loaded = repository.load()

            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0].transaction_id, "T001")
            self.assertEqual(loaded[1].transaction_id, "T002")
            self.assertTrue(path.exists())

# test for load returns empty when file missing
    def test_load_returns_empty_when_file_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "transactions.json"
            repository = TransactionRepository(str(path))
            self.assertEqual(repository.load(), [])

    # test for load raises when json is malformed
    def test_load_raises_when_json_is_malformed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "transactions.json"
            path.write_text("{ invalid json }", encoding="utf-8")
            repository = TransactionRepository(str(path))
            with self.assertRaises(json.JSONDecodeError):
                repository.load()

# test for load parses sale and expense records
    def test_load_parses_sale_and_expense_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "transactions.json"
            data = [
                {
                    "transaction_id": "T001",
                    "amount": 100.0,
                    "created_at": datetime.now().isoformat(),
                    "description": "Sale",
                    "transaction_type": "sale",
                    "related_order_id": "CO001",
                },
                {
                    "transaction_id": "T002",
                    "amount": 40.0,
                    "created_at": datetime.now().isoformat(),
                    "description": "Expense",
                    "transaction_type": "expense",
                    "related_order_id": "PO001",
                },
            ]
            with path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            repository = TransactionRepository(str(path))
            loaded = repository.load()
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0].transaction_type().value, "sale")
            self.assertEqual(loaded[1].transaction_type().value, "expense")
            self.assertEqual(loaded[0].related_order_id, "CO001")


if __name__ == "__main__":
    unittest.main()
