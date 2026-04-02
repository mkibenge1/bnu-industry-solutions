import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from models.bnu_models import ExpenseTransaction, SaleTransaction
from services.finance_service import FinanceService


class TestFinanceService(unittest.TestCase):
# test for record sale and expense totals
    @patch("services.finance_service.TransactionRepository")
    # test for record sale and expense totals
    def test_record_sale_and_expense_totals(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = FinanceService()

        service.record_sale(100.0, "Sale #1", "CO001")
        service.record_expense(40.0, "Purchase stock", "PO001")

        self.assertEqual(service.total_sales(), 100.0)
        self.assertEqual(service.total_expenses(), 40.0)
        self.assertEqual(service.profit(), 60.0)

        transactions = service.get_all_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].amount, 100.0)
        self.assertEqual(isinstance(transactions[0], SaleTransaction), True)
        self.assertEqual(isinstance(transactions[1], ExpenseTransaction), True)

# test for export transactions csv falls back to csv writer
    @patch("services.finance_service.TransactionRepository")
    # test for export transactions csv falls back to csv writer
    def test_export_transactions_csv_falls_back_to_csv_writer(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = FinanceService()
        service.record_sale(50.0, "Sale #2", "CO002")

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "transactions.csv"
            exported_path = service.export_transactions_csv(str(csv_path))
            self.assertEqual(str(csv_path), exported_path)
            self.assertTrue(csv_path.exists())
            self.assertIn("transaction_id", csv_path.read_text())

# test for get sales and expense transactions
    @patch("services.finance_service.TransactionRepository")
    # test for get sales and expense transactions
    def test_get_sales_and_expense_transactions(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = FinanceService()
        service.record_sale(75.0, "Sale", "CO001")
        service.record_expense(25.0, "Expense", "PO001")

        self.assertEqual(len(service.get_sales_transactions()), 1)
        self.assertEqual(len(service.get_expense_transactions()), 1)
        self.assertEqual(service.get_sales_transactions()[0].amount, 75.0)
        self.assertEqual(service.get_expense_transactions()[0].amount, 25.0)

# test for plot financial summary raises when no transactions
    @patch("services.finance_service.TransactionRepository")
    # test for plot financial summary raises when no transactions
    def test_plot_financial_summary_raises_when_no_transactions(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = FinanceService()
        with self.assertRaises(ValueError):
            service.plot_financial_summary("data/unused.png")

    # test for export transactions csv uses pandas
    @patch("services.finance_service.TransactionRepository")
    # test for export transactions csv uses pandas
    def test_export_transactions_csv_uses_pandas(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = FinanceService()
        service.record_sale(50.0, "Sale #2", "CO002")

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "transactions.csv"
            exported_path = service.export_transactions_csv(str(csv_path))

            self.assertEqual(str(csv_path), exported_path)
            self.assertTrue(csv_path.exists())
            self.assertIn("transaction_id", csv_path.read_text())
            self.assertIn("Sale #2", csv_path.read_text())

    # test for plot financial summary generates image file
    @patch("services.finance_service.TransactionRepository")
    # test for plot financial summary generates image file
    def test_plot_financial_summary_generates_image_file(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = FinanceService()
        service.record_sale(75.0, "Sale", "CO001")
        service.record_expense(25.0, "Expense", "PO001")

        os.environ["MPLBACKEND"] = "Agg"
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "financial_summary.png"
            exported_path = service.plot_financial_summary(str(image_path))

            self.assertEqual(str(image_path), exported_path)
            self.assertTrue(image_path.exists())
            self.assertGreater(image_path.stat().st_size, 0)

    # test for transaction id generation uses max existing id
    @patch("services.finance_service.TransactionRepository")
    # test for transaction id generation uses max existing id
    def test_transaction_id_generation_uses_max_existing_id(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.save = Mock()
        mock_repo.load.return_value = [
            SaleTransaction("T001", 10.0, __import__("datetime").datetime.now(), "old sale", "CO001"),
            ExpenseTransaction("T003", 5.0, __import__("datetime").datetime.now(), "old expense", "PO001"),
        ]

        service = FinanceService()
        new_transaction = service.record_sale(12.0, "New sale", "CO002")
        self.assertEqual(new_transaction.transaction_id, "T004")


if __name__ == "__main__":
    unittest.main()
