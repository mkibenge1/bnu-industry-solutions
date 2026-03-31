import json
from datetime import datetime
from pathlib import Path

from models.bnu_models import (
    CustomerOrder,
    OrderLine,
    OrderStatus,
    PurchaseOrder,
)


# Store orders in a JSON file for reuse
class OrderRepository:
    # Make sure the data folder exists
    def __init__(self, file_path: str) -> None:
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def save_purchase_orders(self, orders: list[PurchaseOrder]) -> None:
        order_data = []

        # Convert each purchase order into simple JSON
        for order in orders:
            order_data.append(
                {
                    "order_id": order.order_id,
                    "created_at": order.created_at.isoformat(),
                    "status": order.status.value,
                    "supplier_id": order.supplier_id,
                    "expected_delivery_date": (
                        order.expected_delivery_date.isoformat()
                        if order.expected_delivery_date is not None
                        else None
                    ),
                    "lines": [
                        {
                            "product_id": line.product_id,
                            "quantity": line.quantity,
                            "unit_price": line.unit_price,
                        }
                        for line in order.lines
                    ],
                }
            )

        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(order_data, file, indent=4)

    # Load purchase orders from the JSON file
    def load_purchase_orders(self) -> list[PurchaseOrder]:
        if not self._file_path.exists():
            return []

        with self._file_path.open("r", encoding="utf-8") as file:
            order_data = json.load(file)

        orders: list[PurchaseOrder] = []

        # Rebuild purchase order objects from stored values
        for item in order_data:
            order = PurchaseOrder(
                order_id=item["order_id"],
                created_at=datetime.fromisoformat(item["created_at"]),
                status=OrderStatus(item["status"]),
                supplier_id=item["supplier_id"],
                expected_delivery_date=(
                    datetime.fromisoformat(item["expected_delivery_date"])
                    if item["expected_delivery_date"] is not None
                    else None
                ),
            )

            for line_data in item["lines"]:
                order.add_line(
                    OrderLine(
                        product_id=line_data["product_id"],
                        quantity=line_data["quantity"],
                        unit_price=line_data["unit_price"],
                    )
                )

            orders.append(order)

        return orders

    def save_customer_orders(self, orders: list[CustomerOrder]) -> None:
        order_data = []

        # Convert each customer order into simple JSON
        for order in orders:
            order_data.append(
                {
                    "order_id": order.order_id,
                    "created_at": order.created_at.isoformat(),
                    "status": order.status.value,
                    "customer_name": order.customer_name,
                    "customer_email": order.customer_email,
                    "lines": [
                        {
                            "product_id": line.product_id,
                            "quantity": line.quantity,
                            "unit_price": line.unit_price,
                        }
                        for line in order.lines
                    ],
                }
            )

        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(order_data, file, indent=4)

    # Load customer orders from the JSON file
    def load_customer_orders(self) -> list[CustomerOrder]:
        if not self._file_path.exists():
            return []

        with self._file_path.open("r", encoding="utf-8") as file:
            order_data = json.load(file)

        orders: list[CustomerOrder] = []

        # Rebuild customer order objects from stored values
        for item in order_data:
            order = CustomerOrder(
                order_id=item["order_id"],
                created_at=datetime.fromisoformat(item["created_at"]),
                status=OrderStatus(item["status"]),
                customer_name=item["customer_name"],
                customer_email=item["customer_email"],
            )

            for line_data in item["lines"]:
                order.add_line(
                    OrderLine(
                        product_id=line_data["product_id"],
                        quantity=line_data["quantity"],
                        unit_price=line_data["unit_price"],
                    )
                )
            orders.append(order)
        return orders