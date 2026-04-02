import sys
import unittest
from io import StringIO
from unittest.mock import Mock, patch

from models.bnu_models import ExpenseTransaction, Product, SaleTransaction, Supplier, TransactionType
from ui.menu import Menu


class TestMenu(unittest.TestCase):
    def setUp(self):
        self.menu = Menu(Mock(), Mock(), Mock(), Mock())

# test for prompt name valid
    @patch("builtins.input", side_effect=["John Doe"])
    # test for prompt name valid
    def test_prompt_name_valid(self, mock_input):
        self.assertEqual(self.menu._prompt_name("Name: "), "John Doe")

# test for prompt email retries on invalid
    @patch("builtins.input", side_effect=["jane@", "jane@example.com"])
    # test for prompt email retries on invalid
    def test_prompt_email_retries_on_invalid(self, mock_input):
        stdout = StringIO()
        with patch("sys.stdout", new=stdout):
            result = self.menu._prompt_email("Email: ")
        self.assertEqual(result, "jane@example.com")
        self.assertIn("Enter a valid email address", stdout.getvalue())

# test for prompt int retries until valid
    @patch("builtins.input", side_effect=["abc", "10"])
    # test for prompt int retries until valid
    def test_prompt_int_retries_until_valid(self, mock_input):
        stdout = StringIO()
        with patch("sys.stdout", new=stdout):
            result = self.menu._prompt_int("Number: ")
        self.assertEqual(result, 10)
        self.assertIn("Enter a valid integer", stdout.getvalue())

# test for prompt float retries until valid
    @patch("builtins.input", side_effect=["not-a-number", "3.14"])
    # test for prompt float retries until valid
    def test_prompt_float_retries_until_valid(self, mock_input):
        stdout = StringIO()
        with patch("sys.stdout", new=stdout):
            result = self.menu._prompt_float("Value: ")
        self.assertEqual(result, 3.14)
        self.assertIn("Enter a valid number", stdout.getvalue())

# test for prompt text uses default
    @patch("builtins.input", side_effect=["", "Default"])
    # test for prompt text uses default
    def test_prompt_text_uses_default(self, mock_input):
        self.assertEqual(self.menu._prompt_text("Text: ", default="Default"), "Default")

# test for prompt phone retries until valid
    @patch("builtins.input", side_effect=["abc123", "0123456789"])
    # test for prompt phone retries until valid
    def test_prompt_phone_retries_until_valid(self, mock_input):
        stdout = StringIO()
        with patch("sys.stdout", new=stdout):
            result = self.menu._prompt_phone("Phone: ")
        self.assertEqual(result, "0123456789")
        self.assertIn("Enter a valid phone number", stdout.getvalue())

# test for prompt lookup supplier id returns supplier
    @patch("builtins.input", side_effect=["S999"])
    # test for prompt lookup supplier id returns supplier
    def test_prompt_lookup_supplier_id_returns_supplier(self, mock_input):
        supplier_service = Mock()
        supplier_service.get_supplier_by_id.return_value = True
        menu = Menu(supplier_service, Mock(), Mock(), Mock())
        self.assertEqual(menu._prompt_lookup_supplier_id("Supplier: "), "S999")

# test for prompt lookup product id returns product
    @patch("builtins.input", side_effect=["P999"])
    # test for prompt lookup product id returns product
    def test_prompt_lookup_product_id_returns_product(self, mock_input):
        inventory_service = Mock()
        inventory_service.get_product_by_id.return_value = True
        menu = Menu(Mock(), inventory_service, Mock(), Mock())
        self.assertEqual(menu._prompt_lookup_product_id("Product: "), "P999")

# test for prompt lookup order id returns customer order
    @patch("builtins.input", side_effect=["CO999"])
    # test for prompt lookup order id returns customer order
    def test_prompt_lookup_order_id_returns_customer_order(self, mock_input):
        order_service = Mock()
        order_service.get_customer_order_by_id.return_value = True
        menu = Menu(Mock(), Mock(), order_service, Mock())
        self.assertEqual(menu._prompt_lookup_order_id("Order: ", "customer"), "CO999")

# test for print order outputs order data
    @patch("sys.stdout", new_callable=StringIO)
    # test for print order outputs order data
    def test_print_order_outputs_order_data(self, mock_stdout):
        order = Mock()
        order.order_id = "CO001"
        order.status.value = "pending"
        order.created_at = __import__("datetime").datetime(2025, 1, 1, 10, 0)
        order.order_type.return_value = "customer"
        order.customer_name = "Alice"
        order.customer_email = "alice@example.com"
        line = Mock()
        line.product_id = "P001"
        line.quantity = 2
        line.unit_price = 3.5
        line.line_total.return_value = 7.0
        order.lines = [line]
        order.total_amount.return_value = 7.0

        self.menu._print_order(order)
        output = mock_stdout.getvalue()
        self.assertIn("Order ID: CO001", output)
        self.assertIn("Customer: Alice <alice@example.com>", output)
        self.assertIn("Product ID", output)
        self.assertIn("£7.00", output)

# test for run menu reprompts for non digit option
    @patch("builtins.input", side_effect=["x", "1"])
    # test for run menu reprompts for non digit option
    def test_run_menu_reprompts_for_non_digit_option(self, mock_input):
        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu._run_menu("TEST", [("Exit", None)])
        self.assertIn("Invalid option", output.getvalue())

# test for format table outputs header and row
    def test_format_table_outputs_header_and_row(self):
        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu._format_table(["A", "B"], [["x", 1]])

        self.assertIn("A | B", output.getvalue())
        self.assertIn("x | 1", output.getvalue())

# test for run exits on exit option
    @patch("builtins.input", side_effect=["6"])
    # test for run exits on exit option
    def test_run_exits_on_exit_option(self, mock_input):
        stdout = StringIO()
        with patch("sys.stdout", new=stdout):
            self.menu.run()
        self.assertIn("Exiting system", stdout.getvalue())

    # test for view suppliers prints table
    def test_view_suppliers_prints_table(self):
        supplier = Supplier(
            supplier_id="S001",
            name="Acme Supplies",
            contact_name="Jane Doe",
            email="jane@example.com",
            phone="0123456789",
            address="10 Test Street",
        )
        self.menu.supplier_service.list_active_suppliers.return_value = [supplier]

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.view_suppliers()

        self.assertIn("Acme Supplies", output.getvalue())
        self.assertIn("0123456789", output.getvalue())

    # test for view products prints table
    def test_view_products_prints_table(self):
        product = Product(
            product_id="P001",
            name="Widget",
            description="A sample widget",
            unit_price=5.0,
            stock_quantity=10,
            reorder_level=2,
            supplier_id="S001",
        )
        self.menu.inventory_service.list_products.return_value = [product]

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.view_products()

        self.assertIn("Widget", output.getvalue())
        self.assertIn("£5.00", output.getvalue())

    # test for view low stock prints alerts
    def test_view_low_stock_prints_alerts(self):
        product = Product(
            product_id="P001",
            name="Widget",
            description="A sample widget",
            unit_price=5.0,
            stock_quantity=2,
            reorder_level=5,
            supplier_id="S001",
        )
        self.menu.inventory_service.low_stock_products.return_value = [product]

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.view_low_stock()

        self.assertIn("LOW STOCK ALERTS", output.getvalue())
        self.assertIn("Widget", output.getvalue())

    # test for view financial summary prints totals
    def test_view_financial_summary_prints_totals(self):
        self.menu.finance_service.total_sales.return_value = 100.0
        self.menu.finance_service.total_expenses.return_value = 40.0
        self.menu.finance_service.profit.return_value = 60.0

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.view_financial_summary()

        self.assertIn("Total Sales: £100.00", output.getvalue())
        self.assertIn("Total Expenses: £40.00", output.getvalue())
        self.assertIn("Profit: £60.00", output.getvalue())

    # test for view sales transactions prints rows
    def test_view_sales_transactions_prints_rows(self):
        transaction = SaleTransaction(
            transaction_id="T001",
            amount=75.0,
            created_at=__import__("datetime").datetime.now(),
            description="Sale",
            related_order_id="CO001",
        )
        self.menu.finance_service.get_sales_transactions.return_value = [transaction]

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.view_sales_transactions()

        self.assertIn("SALE", output.getvalue())
        self.assertIn("£75.00", output.getvalue())

    # test for view expense transactions prints rows
    def test_view_expense_transactions_prints_rows(self):
        transaction = ExpenseTransaction(
            transaction_id="T002",
            amount=25.0,
            created_at=__import__("datetime").datetime.now(),
            description="Expense",
            related_order_id="PO001",
        )
        self.menu.finance_service.get_expense_transactions.return_value = [transaction]

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.view_expense_transactions()

        self.assertIn("EXPENSE", output.getvalue())
        self.assertIn("£25.00", output.getvalue())

    # test for view financial transactions prints rows
    def test_view_financial_transactions_prints_rows(self):
        transaction = SaleTransaction(
            transaction_id="T003",
            amount=30.0,
            created_at=__import__("datetime").datetime.now(),
            description="Sale detail",
            related_order_id="CO002",
        )
        self.menu.finance_service.get_all_transactions.return_value = [transaction]

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.view_financial_transactions()

        self.assertIn("Sale detail", output.getvalue())
        self.assertIn("£30.00", output.getvalue())

# test for create customer order flow with quantity retry
    @patch("builtins.input", side_effect=["Alice", "alice@example.com", "P001", "99", "2"])
    # test for create customer order flow retries quantity then succeeds
    def test_create_customer_order_flow_retries_quantity_then_succeeds(self, mock_input):
        product = Product(
            product_id="P001",
            name="Widget",
            description="A widget",
            unit_price=5.0,
            stock_quantity=10,
            reorder_level=3,
            supplier_id="S001",
        )
        self.menu.inventory_service.get_product_by_id.return_value = product

        created_order = Mock()
        created_order.order_id = "CO001"
        self.menu.order_service.create_customer_order.return_value = created_order

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.create_customer_order()

        self.menu.order_service.create_customer_order.assert_called_once()
        self.assertIn("Only 10 units are available", output.getvalue())
        self.assertIn("Customer order created with ID: CO001", output.getvalue())

# test for create purchase order flow retries after service error
    @patch("builtins.input", side_effect=["S001", "P001", "2", "S001", "P001", "2"])
    # test for create purchase order flow retries after error
    def test_create_purchase_order_flow_retries_after_error(self, mock_input):
        product = Product(
            product_id="P001",
            name="Widget",
            description="A widget",
            unit_price=5.0,
            stock_quantity=10,
            reorder_level=3,
            supplier_id="S001",
        )
        self.menu.supplier_service.get_supplier_by_id.return_value = Mock()
        self.menu.inventory_service.get_product_by_id.return_value = product

        created_order = Mock()
        created_order.order_id = "PO001"
        self.menu.order_service.create_purchase_order.side_effect = [ValueError("bad request"), created_order]

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.create_purchase_order()

        self.assertEqual(self.menu.order_service.create_purchase_order.call_count, 2)
        self.assertIn("Error: bad request", output.getvalue())
        self.assertIn("Purchase order created with ID: PO001", output.getvalue())

# test for update customer order flow with line update and quantity retry
    @patch("builtins.input", side_effect=["CO001", "", "", "y", "P001", "5", "2"])
    # test for update customer order flow with line update retry
    def test_update_customer_order_flow_with_line_update_retry(self, mock_input):
        existing_order = Mock()
        existing_order.order_id = "CO001"
        existing_order.customer_name = "Alice"
        existing_order.customer_email = "alice@example.com"
        existing_line = Mock()
        existing_line.product_id = "P001"
        existing_line.quantity = 1
        existing_order.lines = [existing_line]

        product = Product(
            product_id="P001",
            name="Widget",
            description="A widget",
            unit_price=5.0,
            stock_quantity=2,
            reorder_level=1,
            supplier_id="S001",
        )

        self.menu.order_service.get_customer_order_by_id.return_value = existing_order
        self.menu.inventory_service.get_product_by_id.return_value = product
        self.menu.order_service.get_customer_order_by_id.return_value = existing_order

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.update_customer_order()

        self.menu.order_service.update_customer_order.assert_called_once()
        _, kwargs = self.menu.order_service.update_customer_order.call_args
        self.assertEqual(kwargs["order_id"], "CO001")
        self.assertEqual(kwargs["lines"][0].quantity, 2)
        self.assertIn("Only 3 total units are available", output.getvalue())

# test for delete customer order flow retries after service error
    @patch("builtins.input", side_effect=["CO001", "CO001"])
    # test for delete customer order flow retries after error
    def test_delete_customer_order_flow_retries_after_error(self, mock_input):
        self.menu.order_service.get_customer_order_by_id.return_value = Mock(order_id="CO001")
        self.menu.order_service.delete_customer_order.side_effect = [ValueError("locked"), None]

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.delete_customer_order()

        self.assertEqual(self.menu.order_service.delete_customer_order.call_count, 2)
        self.assertIn("Error: locked", output.getvalue())
        self.assertIn("Customer order deleted successfully.", output.getvalue())

# test for run menu navigates into customers submenu and exits
    @patch("builtins.input", side_effect=["1", "6"])
    # test for run navigates to customers menu then exits
    def test_run_navigates_to_customers_menu_then_exits(self, mock_input):
        self.menu._run_customers_menu = Mock()

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.run()

        self.menu._run_customers_menu.assert_called_once()
        self.assertIn("Exiting system", output.getvalue())

# test for run menu navigates to orders submenu and exits
    @patch("builtins.input", side_effect=["2", "6"])
    # test for run navigates to orders menu then exits
    def test_run_navigates_to_orders_menu_then_exits(self, mock_input):
        self.menu._run_orders_menu = Mock()

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.run()

        self.menu._run_orders_menu.assert_called_once()
        self.assertIn("Exiting system", output.getvalue())

# test for delete supplier flow retries after service error
    @patch("builtins.input", side_effect=["S001", "S001"])
    # test for delete supplier flow retries after error
    def test_delete_supplier_flow_retries_after_error(self, mock_input):
        self.menu.supplier_service.get_supplier_by_id.return_value = Mock(supplier_id="S001")
        self.menu.supplier_service.delete_supplier.side_effect = [ValueError("in use"), None]

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.delete_supplier()

        self.assertEqual(self.menu.supplier_service.delete_supplier.call_count, 2)
        self.assertIn("Error: in use", output.getvalue())
        self.assertIn("Supplier deleted successfully.", output.getvalue())

# test for run menu navigates to suppliers submenu and exits
    @patch("builtins.input", side_effect=["3", "6"])
    # test for run navigates to suppliers menu then exits
    def test_run_navigates_to_suppliers_menu_then_exits(self, mock_input):
        self.menu._run_suppliers_menu = Mock()

        output = StringIO()
        with patch("sys.stdout", new=output):
            self.menu.run()

        self.menu._run_suppliers_menu.assert_called_once()
        self.assertIn("Exiting system", output.getvalue())


if __name__ == "__main__":
    unittest.main()
