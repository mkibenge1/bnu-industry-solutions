import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from models.bnu_models import CustomerOrder, OrderLine, OrderStatus, PurchaseOrder
from repositories.order_repository import OrderRepository


class TestOrderRepository(unittest.TestCase):
# test for save and load purchase and customer orders
    def test_save_and_load_purchase_and_customer_orders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            purchase_path = Path(temp_dir) / "purchase_orders.json"
            customer_path = Path(temp_dir) / "customer_orders.json"

            purchase_repo = OrderRepository(str(purchase_path))
            customer_repo = OrderRepository(str(customer_path))

            purchase_order = PurchaseOrder(
                order_id="PO001",
                created_at=datetime.now(),
                supplier_id="S001",
            )
            purchase_order.add_line(OrderLine(product_id="P001", quantity=2, unit_price=4.0))

            customer_order = CustomerOrder(
                order_id="CO001",
                created_at=datetime.now(),
                customer_name="Alice",
                customer_email="alice@example.com",
            )
            customer_order.add_line(OrderLine(product_id="P002", quantity=1, unit_price=7.5))

            purchase_repo.save_purchase_orders([purchase_order])
            customer_repo.save_customer_orders([customer_order])

            loaded_purchase = purchase_repo.load_purchase_orders()
            loaded_customer = customer_repo.load_customer_orders()

            self.assertEqual(len(loaded_purchase), 1)
            self.assertEqual(len(loaded_customer), 1)
            self.assertEqual(loaded_purchase[0].order_id, "PO001")
            self.assertEqual(loaded_customer[0].order_id, "CO001")
            self.assertTrue(purchase_path.exists())
            self.assertTrue(customer_path.exists())

# test for save and load purchase order with expected delivery date
    def test_save_and_load_purchase_order_with_expected_delivery_date(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            purchase_path = Path(temp_dir) / "purchase_orders.json"
            purchase_repo = OrderRepository(str(purchase_path))

            purchase_order = PurchaseOrder(
                order_id="PO002",
                created_at=datetime(2025, 1, 1, 9, 0),
                supplier_id="S001",
                expected_delivery_date=datetime(2025, 1, 10, 14, 0),
            )
            purchase_order.add_line(
                OrderLine(product_id="P001", quantity=3, unit_price=4.0)
            )

            purchase_repo.save_purchase_orders([purchase_order])
            loaded = purchase_repo.load_purchase_orders()

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].expected_delivery_date, purchase_order.expected_delivery_date)
            self.assertEqual(loaded[0].order_id, "PO002")

    # test for load purchase orders raises when json is malformed
    def test_load_purchase_orders_raises_when_json_is_malformed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            purchase_path = Path(temp_dir) / "purchase_orders.json"
            purchase_path.write_text("{ invalid json }", encoding="utf-8")
            repository = OrderRepository(str(purchase_path))
            with self.assertRaises(json.JSONDecodeError):
                repository.load_purchase_orders()

    # test for load customer orders raises when json is malformed
    def test_load_customer_orders_raises_when_json_is_malformed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            customer_path = Path(temp_dir) / "customer_orders.json"
            customer_path.write_text("[ invalid json ", encoding="utf-8")
            repository = OrderRepository(str(customer_path))
            with self.assertRaises(json.JSONDecodeError):
                repository.load_customer_orders()

    # test for load purchase orders defaults missing optional fields
    def test_load_purchase_orders_defaults_missing_optional_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            purchase_path = Path(temp_dir) / "purchase_orders.json"
            data = [
                {
                    "order_id": "PO010",
                    "created_at": datetime(2025, 1, 1, 9, 0).isoformat(),
                    "supplier_id": "S001",
                }
            ]
            purchase_path.write_text(json.dumps(data), encoding="utf-8")

            repository = OrderRepository(str(purchase_path))
            loaded = repository.load_purchase_orders()

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].status, OrderStatus.PENDING)
            self.assertIsNone(loaded[0].expected_delivery_date)
            self.assertEqual(loaded[0].lines, [])

    # test for load customer orders defaults missing optional fields
    def test_load_customer_orders_defaults_missing_optional_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            customer_path = Path(temp_dir) / "customer_orders.json"
            data = [
                {
                    "order_id": "CO010",
                    "created_at": datetime(2025, 1, 1, 9, 0).isoformat(),
                }
            ]
            customer_path.write_text(json.dumps(data), encoding="utf-8")

            repository = OrderRepository(str(customer_path))
            loaded = repository.load_customer_orders()

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].status, OrderStatus.PENDING)
            self.assertEqual(loaded[0].customer_name, "")
            self.assertEqual(loaded[0].customer_email, "")
            self.assertEqual(loaded[0].lines, [])


if __name__ == "__main__":
    unittest.main()
