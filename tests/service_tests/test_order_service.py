import unittest
from unittest.mock import Mock, patch

from models.bnu_models import OrderLine, OrderStatus, Product
from services.order_service import OrderService


class TestOrderService(unittest.TestCase):
# test for create customer order reduces stock and records sale
    @patch("services.order_service.OrderRepository")
    # test for create customer order reduces stock and records sale
    def test_create_customer_order_reduces_stock_and_records_sale(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_customer_orders = Mock()
        mock_repo.save_purchase_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=5.0,
            stock_quantity=10,
            reorder_level=3,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        supplier_service = Mock()
        finance_service = Mock()
        finance_service.record_sale = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)
        order = service.create_customer_order(
            customer_name="Alice",
            customer_email="alice@example.com",
            lines=[OrderLine(product_id="P001", quantity=2, unit_price=5.0)],
        )

        self.assertEqual(order.total_amount(), 10.0)
        self.assertEqual(product.stock_quantity, 8)
        finance_service.record_sale.assert_called_once()

# test for create customer order rejects insufficient stock
    @patch("services.order_service.OrderRepository")
    # test for create customer order rejects insufficient stock
    def test_create_customer_order_rejects_insufficient_stock(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_customer_orders = Mock()
        mock_repo.save_purchase_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=5.0,
            stock_quantity=1,
            reorder_level=3,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        finance_service = Mock()

        service = OrderService(inventory_service, Mock(), finance_service)

        with self.assertRaises(ValueError):
            service.create_customer_order(
                customer_name="Alice",
                customer_email="alice@example.com",
                lines=[OrderLine(product_id="P001", quantity=2, unit_price=5.0)],
            )

# test for receive purchase order marks delivered and records expense
    @patch("services.order_service.OrderRepository")
    # test for receive purchase order marks delivered and records expense
    def test_receive_purchase_order_marks_delivered_and_records_expense(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_customer_orders = Mock()
        mock_repo.save_purchase_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=5.0,
            stock_quantity=5,
            reorder_level=3,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        supplier = Mock()
        supplier.is_active = True
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        finance_service = Mock()
        finance_service.record_expense = Mock()
        finance_service.record_sale = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)
        purchase_order = service.create_purchase_order(
            supplier_id="S001",
            lines=[OrderLine(product_id="P001", quantity=2, unit_price=5.0)],
        )

        service.mark_purchase_order_as_shipped(purchase_order.order_id)
        service.receive_purchase_order(purchase_order.order_id)

        self.assertEqual(product.stock_quantity, 7)
        finance_service.record_expense.assert_called_once()

# test for create purchase order and list purchase orders
    @patch("services.order_service.OrderRepository")
    # test for create purchase order and list purchase orders
    def test_create_purchase_order_and_list_purchase_orders(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=4.0,
            stock_quantity=5,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product

        supplier = Mock()
        supplier.is_active = True
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        finance_service = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)
        purchase_order = service.create_purchase_order(
            supplier_id="S001",
            lines=[OrderLine(product_id="P001", quantity=1, unit_price=4.0)],
        )

        self.assertEqual(purchase_order.order_id, "PO001")
        self.assertEqual(len(service.list_purchase_orders()), 1)

# test for delete purchase order rejects non pending
    @patch("services.order_service.OrderRepository")
    # test for delete purchase order rejects non pending
    def test_delete_purchase_order_rejects_non_pending(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=4.0,
            stock_quantity=5,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        supplier = Mock()
        supplier.is_active = True
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        finance_service = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)
        purchase_order = service.create_purchase_order(
            supplier_id="S001",
            lines=[OrderLine(product_id="P001", quantity=1, unit_price=4.0)],
        )
        service.mark_purchase_order_as_shipped(purchase_order.order_id)

        with self.assertRaises(ValueError):
            service.delete_purchase_order(purchase_order.order_id)

# test for update purchase order changes supplier and lines
    @patch("services.order_service.OrderRepository")
    # test for update purchase order changes supplier and lines
    def test_update_purchase_order_changes_supplier_and_lines(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=4.0,
            stock_quantity=5,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product

        supplier = Mock()
        supplier.is_active = True
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        finance_service = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)
        purchase_order = service.create_purchase_order(
            supplier_id="S001",
            lines=[OrderLine(product_id="P001", quantity=1, unit_price=4.0)],
        )

        supplier_service.get_supplier_by_id.return_value = supplier
        service.update_purchase_order(
            order_id=purchase_order.order_id,
            supplier_id="S001",
            lines=[OrderLine(product_id="P001", quantity=2, unit_price=4.0)],
        )

        self.assertEqual(purchase_order.supplier_id, "S001")
        self.assertEqual(len(purchase_order.lines), 1)
        self.assertEqual(purchase_order.lines[0].quantity, 2)

# test for update customer order adjusts stock
    @patch("services.order_service.OrderRepository")
    # test for update customer order adjusts stock
    def test_update_customer_order_adjusts_stock(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=5.0,
            stock_quantity=10,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        finance_service = Mock()
        finance_service.record_sale = Mock()

        service = OrderService(inventory_service, Mock(), finance_service)
        customer_order = service.create_customer_order(
            customer_name="Alice",
            customer_email="alice@example.com",
            lines=[OrderLine(product_id="P001", quantity=1, unit_price=5.0)],
        )

        service.update_customer_order(
            order_id=customer_order.order_id,
            lines=[OrderLine(product_id="P001", quantity=2, unit_price=5.0)],
        )

        self.assertEqual(product.stock_quantity, 8)
        self.assertEqual(customer_order.lines[0].quantity, 2)

# test for delete customer order restores stock
    @patch("services.order_service.OrderRepository")
    # test for delete customer order restores stock
    def test_delete_customer_order_restores_stock(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=5.0,
            stock_quantity=5,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        finance_service = Mock()
        finance_service.record_sale = Mock()

        service = OrderService(inventory_service, Mock(), finance_service)
        customer_order = service.create_customer_order(
            customer_name="Alice",
            customer_email="alice@example.com",
            lines=[OrderLine(product_id="P001", quantity=2, unit_price=5.0)],
        )

        service.delete_customer_order(customer_order.order_id)
        self.assertEqual(product.stock_quantity, 5)

# test for receive purchase order rejects non shipped
    @patch("services.order_service.OrderRepository")
    # test for receive purchase order rejects non shipped
    def test_receive_purchase_order_rejects_non_shipped(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=5.0,
            stock_quantity=5,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        supplier = Mock()
        supplier.is_active = True
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        finance_service = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)
        purchase_order = service.create_purchase_order(
            supplier_id="S001",
            lines=[OrderLine(product_id="P001", quantity=1, unit_price=5.0)],
        )

        with self.assertRaises(ValueError):
            service.receive_purchase_order(purchase_order.order_id)

# test for get purchase order by id returns none when missing
    @patch("services.order_service.OrderRepository")
    # test for get purchase order by id returns none when missing
    def test_get_purchase_order_by_id_returns_none_when_missing(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        service = OrderService(Mock(), Mock(), Mock())
        self.assertIsNone(service.get_purchase_order_by_id("PO999"))

        self.assertIsNone(service.get_customer_order_by_id("CO999"))

    # test for create purchase order rejects empty lines
    @patch("services.order_service.OrderRepository")
    # test for create purchase order rejects empty lines
    def test_create_purchase_order_rejects_empty_lines(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        inventory_service = Mock()
        supplier_service = Mock()
        finance_service = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)

        with self.assertRaises(ValueError):
            service.create_purchase_order("S001", [])

    # test for create customer order rejects empty lines
    @patch("services.order_service.OrderRepository")
    # test for create customer order rejects empty lines
    def test_create_customer_order_rejects_empty_lines(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        inventory_service = Mock()
        finance_service = Mock()

        service = OrderService(inventory_service, Mock(), finance_service)

        with self.assertRaises(ValueError):
            service.create_customer_order("Alice", "alice@example.com", [])

    # test for create purchase order invalid product id
    @patch("services.order_service.OrderRepository")
    # test for create purchase order invalid product id
    def test_create_purchase_order_invalid_product_id(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        supplier = Mock()
        supplier.is_active = True
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = None

        finance_service = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)

        with self.assertRaises(ValueError):
            service.create_purchase_order(
                supplier_id="S001",
                lines=[OrderLine(product_id="P999", quantity=1, unit_price=5.0)],
            )

    # test for create customer order invalid product id
    @patch("services.order_service.OrderRepository")
    # test for create customer order invalid product id
    def test_create_customer_order_invalid_product_id(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_customer_orders = Mock()
        mock_repo.save_purchase_orders = Mock()

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = None

        finance_service = Mock()

        service = OrderService(inventory_service, Mock(), finance_service)

        with self.assertRaises(ValueError):
            service.create_customer_order(
                customer_name="Alice",
                customer_email="alice@example.com",
                lines=[OrderLine(product_id="P999", quantity=1, unit_price=5.0)],
            )

    # test for create purchase order rejects inactive supplier
    @patch("services.order_service.OrderRepository")
    # test for create purchase order rejects inactive supplier
    def test_create_purchase_order_rejects_inactive_supplier(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        supplier = Mock()
        supplier.is_active = False
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        inventory_service = Mock()
        finance_service = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)

        with self.assertRaises(ValueError):
            service.create_purchase_order(
                supplier_id="S001",
                lines=[OrderLine(product_id="P001", quantity=1, unit_price=5.0)],
            )

    # test for update customer order rejects non pending
    @patch("services.order_service.OrderRepository")
    # test for update customer order rejects non pending
    def test_update_customer_order_rejects_non_pending(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=5.0,
            stock_quantity=10,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        finance_service = Mock()
        finance_service.record_sale = Mock()

        service = OrderService(inventory_service, Mock(), finance_service)
        customer_order = service.create_customer_order(
            customer_name="Alice",
            customer_email="alice@example.com",
            lines=[OrderLine(product_id="P001", quantity=1, unit_price=5.0)],
        )
        customer_order.update_status(OrderStatus.SHIPPED)

        with self.assertRaises(ValueError):
            service.update_customer_order(
                order_id=customer_order.order_id,
                customer_name="Alice",
            )

    # test for delete customer order rejects non pending
    @patch("services.order_service.OrderRepository")
    # test for delete customer order rejects non pending
    def test_delete_customer_order_rejects_non_pending(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=5.0,
            stock_quantity=5,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        finance_service = Mock()
        finance_service.record_sale = Mock()

        service = OrderService(inventory_service, Mock(), finance_service)
        customer_order = service.create_customer_order(
            customer_name="Alice",
            customer_email="alice@example.com",
            lines=[OrderLine(product_id="P001", quantity=2, unit_price=5.0)],
        )
        customer_order.update_status(OrderStatus.SHIPPED)

        with self.assertRaises(ValueError):
            service.delete_customer_order(customer_order.order_id)

    # test for update purchase order rejects non pending
    @patch("services.order_service.OrderRepository")
    # test for update purchase order rejects non pending
    def test_update_purchase_order_rejects_non_pending(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=4.0,
            stock_quantity=5,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product

        supplier = Mock()
        supplier.is_active = True
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        finance_service = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)
        purchase_order = service.create_purchase_order(
            supplier_id="S001",
            lines=[OrderLine(product_id="P001", quantity=1, unit_price=4.0)],
        )
        service.mark_purchase_order_as_shipped(purchase_order.order_id)

        with self.assertRaises(ValueError):
            service.update_purchase_order(
                order_id=purchase_order.order_id,
                supplier_id="S001",
                lines=[OrderLine(product_id="P001", quantity=2, unit_price=4.0)],
            )

    # test for update purchase order rejects inactive supplier
    @patch("services.order_service.OrderRepository")
    # test for update purchase order rejects inactive supplier
    def test_update_purchase_order_rejects_inactive_supplier(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=4.0,
            stock_quantity=5,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product

        supplier = Mock()
        supplier.is_active = True
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        finance_service = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)
        purchase_order = service.create_purchase_order(
            supplier_id="S001",
            lines=[OrderLine(product_id="P001", quantity=1, unit_price=4.0)],
        )
        supplier_service.get_supplier_by_id.return_value = Mock(is_active=False)

        with self.assertRaises(ValueError):
            service.update_purchase_order(
                order_id=purchase_order.order_id,
                supplier_id="S002",
            )

    # test for order id generation does not reuse deleted ids
    @patch("services.order_service.OrderRepository")
    # test for order id generation does not reuse deleted ids
    def test_order_id_generation_does_not_reuse_deleted_ids(self, mock_order_repo):
        mock_repo = mock_order_repo.return_value
        mock_repo.load_purchase_orders.return_value = []
        mock_repo.load_customer_orders.return_value = []
        mock_repo.save_purchase_orders = Mock()
        mock_repo.save_customer_orders = Mock()

        product = Product(
            product_id="P001",
            name="Widget",
            description="A product",
            unit_price=5.0,
            stock_quantity=20,
            reorder_level=2,
            supplier_id="S001",
        )

        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = product
        inventory_service.save_products = Mock()

        supplier = Mock()
        supplier.is_active = True
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = supplier

        finance_service = Mock()
        finance_service.record_sale = Mock()
        finance_service.record_expense = Mock()

        service = OrderService(inventory_service, supplier_service, finance_service)

        po1 = service.create_purchase_order("S001", [OrderLine("P001", 1, 5.0)])
        po2 = service.create_purchase_order("S001", [OrderLine("P001", 1, 5.0)])
        service.delete_purchase_order(po1.order_id)
        po3 = service.create_purchase_order("S001", [OrderLine("P001", 1, 5.0)])

        co1 = service.create_customer_order("Alice", "alice@example.com", [OrderLine("P001", 1, 5.0)])
        co2 = service.create_customer_order("Bob", "bob@example.com", [OrderLine("P001", 1, 5.0)])
        service.delete_customer_order(co1.order_id)
        co3 = service.create_customer_order("Cara", "cara@example.com", [OrderLine("P001", 1, 5.0)])

        self.assertEqual(po2.order_id, "PO002")
        self.assertEqual(po3.order_id, "PO003")
        self.assertEqual(co2.order_id, "CO002")
        self.assertEqual(co3.order_id, "CO003")


if __name__ == "__main__":
    unittest.main()
