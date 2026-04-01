from __future__ import annotations

from datetime import datetime

from models.bnu_models import (
    ExpenseTransaction,
    FinancialTransaction,
    SaleTransaction,
    TransactionType,
)
from repositories.transaction_repository import TransactionRepository

class FinanceService:
    def __init__(self) -> None:
        self._transaction_repository = TransactionRepository()
        self._transactions: list[FinancialTransaction] = self._transaction_repository.load()  # Load transactions from JSON

    # Generate a new unique transaction ID
    def _generate_transaction_id(self) -> str:
        return f"T{len(self._transactions) + 1:03}"

    # Record a sale transaction
    def record_sale(
        self,
        amount: float,
        description: str,
        related_order_id: str,
    ) -> SaleTransaction:
        transaction = SaleTransaction(
            transaction_id=self._generate_transaction_id(),
            amount=amount,
            created_at=datetime.now(),
            description=description,
            related_order_id=related_order_id,
        )
        self._transactions.append(transaction)
        self._transaction_repository.save(self._transactions)  # Save transaction to JSON
        return transaction

    # Record an expense transaction
    def record_expense(
        self,
        amount: float,
        description: str,
        related_order_id: str,
    ) -> ExpenseTransaction:
        transaction = ExpenseTransaction(
            transaction_id=self._generate_transaction_id(),
            amount=amount,
            created_at=datetime.now(),
            description=description,
            related_order_id=related_order_id,
        )
        self._transactions.append(transaction)
        self._transaction_repository.save(self._transactions)  # Save transaction to JSON
        return transaction

    # Return all transactions in memory
    def get_all_transactions(self) -> list[FinancialTransaction]:
        return self._transactions.copy()

    # Return only sales transactions
    def get_sales_transactions(self) -> list[SaleTransaction]:
        return [
            transaction
            for transaction in self._transactions
            if transaction.transaction_type() == TransactionType.SALE
        ]

    # Return only expense transactions
    def get_expense_transactions(self) -> list[ExpenseTransaction]:
        return [
            transaction
            for transaction in self._transactions
            if transaction.transaction_type() == TransactionType.EXPENSE
        ]

    # Total amount from sales transactions
    def total_sales(self) -> float:
        return sum(transaction.amount for transaction in self.get_sales_transactions())

    # Total amount from expense transactions
    def total_expenses(self) -> float:
        return sum(
            transaction.amount for transaction in self.get_expense_transactions()
        )

    # Calculate profit from sales minus expenses
    def profit(self) -> float:
        return self.total_sales() - self.total_expenses()