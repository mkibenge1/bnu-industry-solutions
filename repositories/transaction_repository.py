import json
from datetime import datetime
from pathlib import Path

from models.bnu_models import (
    ExpenseTransaction,
    FinancialTransaction,
    SaleTransaction,
    TransactionType,
)


# Store transactions in a JSON file for reuse
class TransactionRepository:
    # Make sure the data folder exists
    def __init__(self, file_path: str = "data/transactions.json") -> None:
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, transactions: list[FinancialTransaction]) -> None:
        transaction_data = []

        # Convert each transaction into simple JSON
        for transaction in transactions:
            transaction_data.append(
                {
                    "transaction_id": transaction.transaction_id,
                    "amount": transaction.amount,
                    "created_at": transaction.created_at.isoformat(),
                    "description": transaction.description,
                    "transaction_type": transaction.transaction_type().value,
                    "related_order_id": transaction.related_order_id,
                }
            )

        # Write file in readable JSON
        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(transaction_data, file, indent=4)

    # Load transactions from the JSON file
    def load(self) -> list[FinancialTransaction]:
        if not self._file_path.exists():
            return []

        with self._file_path.open("r", encoding="utf-8") as file:
            transaction_data = json.load(file)

        transactions: list[FinancialTransaction] = []

        # Rebuild transaction objects from stored values
        for item in transaction_data:
            created_at = datetime.fromisoformat(item["created_at"])
            # Creates object based on transaction type
            if item["transaction_type"] == TransactionType.SALE.value:
                transaction = SaleTransaction(
                    transaction_id=item["transaction_id"],
                    amount=item["amount"],
                    created_at=created_at,
                    description=item["description"],
                    related_order_id=item["related_order_id"],
                )
            else:
                transaction = ExpenseTransaction(
                    transaction_id=item["transaction_id"],
                    amount=item["amount"],
                    created_at=created_at,
                    description=item["description"],
                    related_order_id=item["related_order_id"],
                )

            transactions.append(transaction)

        return transactions