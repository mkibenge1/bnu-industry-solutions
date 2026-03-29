from __future__ import annotations

from datetime import datetime

from models.bnu_models import (
    ExpenseTransaction,
    FinancialTransaction,
    SaleTransaction,
    TransactionType,
)


class FinanceService:
    def __init__(self) -> None:
        self._transactions: list[FinancialTransaction] = []

    def _generate_transaction_id(self) -> str:
        return f"T{len(self._transactions) + 1:03}"

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
        return transaction

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
        return transaction

    def get_all_transactions(self) -> list[FinancialTransaction]:
        return self._transactions.copy()

    def get_sales_transactions(self) -> list[SaleTransaction]:
        return [
            transaction
            for transaction in self._transactions
            if transaction.transaction_type() == TransactionType.SALE
        ]

    def get_expense_transactions(self) -> list[ExpenseTransaction]:
        return [
            transaction
            for transaction in self._transactions
            if transaction.transaction_type() == TransactionType.EXPENSE
        ]

    def total_sales(self) -> float:
        return sum(transaction.amount for transaction in self.get_sales_transactions())

    def total_expenses(self) -> float:
        return sum(
            transaction.amount for transaction in self.get_expense_transactions()
        )

    def profit(self) -> float:
        return self.total_sales() - self.total_expenses()