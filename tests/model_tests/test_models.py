import unittest
from datetime import datetime

from models.bnu_models import (
    CustomerOrder,
    ExpenseTransaction,
    OrderLine,
    OrderStatus,
    Product,
    PurchaseOrder,
    SaleTransaction,
    Supplier,
    TransactionType,
)


class TestProductModel(unittest.TestCase):
# test for stock adjustment
    def test_stock_adjustment(self):
        product = Product(
            product_id="P001",
            name="Test Widget",
            description="A test widget",
            unit_price=5.0,
            stock_quantity=10,
            reorder_level=5,
            supplier_id="S001",
        )

        product.increase_stock(5)
        self.assertEqual(product.stock_quantity, 15)

        product.reduce_stock(3)
        self.assertEqual(product.stock_quantity, 12)

# test for low stock detection
    def test_low_stock_detection(self):
        product = Product(
            product_id="P002",
            name="Low Stock Item",
            description="Needs restock",
            unit_price=2.5,
            stock_quantity=5,
            reorder_level=5,
            supplier_id="S001",
        )
        self.assertTrue(product.is_low_stock())

        product.stock_quantity = 6
        self.assertFalse(product.is_low_stock())

# test for increase stock invalid quantity
    def test_increase_stock_invalid_quantity(self):
        product = Product(
            product_id="P004",
            name="Invalid Increase",
            description="Invalid operation",
            unit_price=1.0,
            stock_quantity=5,
            reorder_level=2,
            supplier_id="S001",
        )
        with self.assertRaises(ValueError):
            product.increase_stock(0)

# test for reduce stock invalid quantity
    def test_reduce_stock_invalid_quantity(self):
        product = Product(
            product_id="P003",
            name="Invalid Item",
            description="Invalid stock operations",
            unit_price=1.0,
            stock_quantity=2,
            reorder_level=1,
            supplier_id="S001",
        )
        with self.assertRaises(ValueError):
            product.reduce_stock(3)


class TestOrderLineModel(unittest.TestCase):
# test for line total
    def test_line_total(self):
        line = OrderLine(product_id="P001", quantity=4, unit_price=2.5)
        self.assertEqual(line.line_total(), 10.0)


class TestOrderModels(unittest.TestCase):
# test for customer order total
    def test_customer_order_total(self):
        order = CustomerOrder(
            order_id="CO001",
            created_at=__import__("datetime").datetime.now(),
            customer_name="Alice",
            customer_email="alice@example.com",
        )
        order.add_line(OrderLine(product_id="P001", quantity=2, unit_price=3.0))
        order.add_line(OrderLine(product_id="P002", quantity=1, unit_price=7.5))
        self.assertEqual(order.total_amount(), 13.5)

# test for purchase order total
    def test_purchase_order_total(self):
        order = PurchaseOrder(
            order_id="PO001",
            created_at=__import__("datetime").datetime.now(),
            supplier_id="S001",
        )
        order.add_line(OrderLine(product_id="P001", quantity=3, unit_price=4.0))
        self.assertEqual(order.total_amount(), 12.0)

# test for order status defaults
    def test_order_status_defaults(self):
        order = PurchaseOrder(
            order_id="PO002",
            created_at=datetime.now(),
            supplier_id="S001",
        )
        self.assertEqual(order.status, OrderStatus.PENDING)

# test for order update status
    def test_order_update_status(self):
        order = PurchaseOrder(
            order_id="PO003",
            created_at=datetime.now(),
            supplier_id="S001",
        )
        order.update_status(OrderStatus.SHIPPED)
        self.assertEqual(order.status, OrderStatus.SHIPPED)

# test for order add line validation
    def test_order_add_line_validation(self):
        order = CustomerOrder(
            order_id="CO002",
            created_at=datetime.now(),
            customer_name="Bob",
            customer_email="bob@example.com",
        )
        with self.assertRaises(ValueError):
            order.add_line(OrderLine(product_id="P001", quantity=0, unit_price=2.0))
        with self.assertRaises(ValueError):
            order.add_line(OrderLine(product_id="P001", quantity=1, unit_price=-1.0))


class TestFinancialTransactionModel(unittest.TestCase):
# test for sale transaction report row
    def test_sale_transaction_report_row(self):
        transaction = SaleTransaction(
            transaction_id="T001",
            amount=123.45,
            created_at=datetime(2025, 12, 31, 10, 0),
            description="Year end sale",
            related_order_id="CO001",
        )
        row = transaction.to_report_row()
        self.assertIn("2025-12-31", row)
        self.assertIn("SALE", row)
        self.assertIn("£123.45", row)
        self.assertEqual(transaction.transaction_type(), TransactionType.SALE)

# test for expense transaction type
    def test_expense_transaction_type(self):
        transaction = ExpenseTransaction(
            transaction_id="T002",
            amount=50.0,
            created_at=datetime.now(),
            description="Stock purchase",
            related_order_id="PO001",
        )
        self.assertEqual(transaction.transaction_type(), TransactionType.EXPENSE)


class TestSupplierModel(unittest.TestCase):
# test for supplier creation
    def test_supplier_creation(self):
        supplier = Supplier(
            supplier_id="S001",
            name="Test Supplier",
            contact_name="Bob Jones",
            email="bob@example.com",
            phone="0123456789",
            address="1 Test Street",
        )
        self.assertEqual(supplier.supplier_id, "S001")
        self.assertTrue(supplier.is_active)


if __name__ == "__main__":
    unittest.main()
