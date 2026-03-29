from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

# Added enum for order status
class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Added enum for transaction types
class TransactionType(Enum):
    SALE = "sale"
    EXPENSE = "expense"

# Data models for suppliers, products, orders, and transactions
@dataclass
class Supplier:
    supplier_id: str
    name: str
    contact_name: str
    email: str
    phone: str
    address: str
    is_active: bool = True


@dataclass
class Product:
    product_id: str
    name: str
    description: str
    unit_price: float
    stock_quantity: int
    reorder_level: int
    supplier_id: str

    def increase_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        self.stock_quantity += quantity

    def reduce_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if quantity > self.stock_quantity:
            raise ValueError("Not enough stock available.")
        self.stock_quantity -= quantity

    def is_low_stock(self) -> bool:
        return self.stock_quantity <= self.reorder_level


@dataclass
class OrderLine:
    product_id: str
    quantity: int
    unit_price: float

    def line_total(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Order(ABC):
    order_id: str
    created_at: datetime
    status: OrderStatus = OrderStatus.PENDING
    lines: list[OrderLine] = field(default_factory=list)

    def add_line(self, line: OrderLine) -> None:
        if line.quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if line.unit_price < 0:
            raise ValueError("Price cannot be negative.")
        self.lines.append(line)

    def total_amount(self) -> float:
        return sum(line.line_total() for line in self.lines)

    def update_status(self, new_status: OrderStatus) -> None:
        self.status = new_status

    @abstractmethod
    def order_type(self) -> str:
        pass


@dataclass
class PurchaseOrder(Order):
    supplier_id: str = ""
    expected_delivery_date: Optional[datetime] = None

    def order_type(self) -> str:
        return "purchase"


@dataclass
class CustomerOrder(Order):
    customer_name: str = ""
    customer_email: str = ""

    def order_type(self) -> str:
        return "customer"


@dataclass
class FinancialTransaction(ABC):
    transaction_id: str
    amount: float
    created_at: datetime
    description: str

    @abstractmethod
    def transaction_type(self) -> TransactionType:
        pass

    def to_report_row(self) -> str:
        return (
            f"{self.created_at.date()} | {self.transaction_type().value.upper()} | "
            f"£{self.amount:.2f} | {self.description}"
        )


@dataclass
class SaleTransaction(FinancialTransaction):
    related_order_id: str = ""

    def transaction_type(self) -> TransactionType:
        return TransactionType.SALE


@dataclass
class ExpenseTransaction(FinancialTransaction):
    related_order_id: str = ""

    def transaction_type(self) -> TransactionType:
        return TransactionType.EXPENSE