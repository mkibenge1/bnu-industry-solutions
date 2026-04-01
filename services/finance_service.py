from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

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
    
    # Prepare transaction data for CSV export
    def _transaction_records(self) -> list[dict[str, str | float]]:
        return [
            {
                "transaction_id": transaction.transaction_id,
                "amount": transaction.amount,
                "created_at": transaction.created_at.isoformat(),
                "description": transaction.description,
                "transaction_type": transaction.transaction_type().value,
                "related_order_id": transaction.related_order_id,
            }
            for transaction in self._transactions
        ]
    
    # Export all transactions to CSV and return file path
    def export_transactions_csv(self, file_path: str = "data/transactions.csv") -> str:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import pandas as pd
            df = pd.DataFrame(self._transaction_records())
            df.to_csv(path, index=False)
        except ImportError:
            with path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "transaction_id",
                        "amount",
                        "created_at",
                        "description",
                        "transaction_type",
                        "related_order_id",
                    ],
                )
                writer.writeheader()
                writer.writerows(self._transaction_records())

        return str(path)
    # Create bar chart for sales v expenses by date
    def plot_financial_summary(self, file_path: str = "data/financial_summary.png") -> str:
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
        except ImportError as error:
            raise ImportError("pandas and matplotlib are required for chart generation") from error

        records = self._transaction_records()
        if not records:
            raise ValueError("No transactions available to plot.")
        # Create dataframe and prepare for plotting
        df = pd.DataFrame(records)
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["amount"] = df["amount"].astype(float)
        df["date"] = df["created_at"].dt.date
        df["type"] = df["transaction_type"].str.upper()

        summary = df.groupby(["date", "type"])["amount"].sum().unstack(fill_value=0)
        for label in ["SALE", "EXPENSE"]:
            if label not in summary.columns:
                summary[label] = 0.0
        summary = summary[["SALE", "EXPENSE"]]
        # Plotting 
        ax = summary.plot(
            kind="bar",
            figsize=(10, 6),
            rot=45,
            title="Sales vs Expenses by Date",
            ylabel="Amount (£)",
            xlabel="Date",
        )
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
        ax.legend(title="Type")
        fig = ax.get_figure()
        fig.tight_layout()

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path)
        plt.close(fig)

        return str(path)