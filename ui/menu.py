from models.bnu_models import OrderLine


class Menu:
    def __init__(
        self,
        supplier_service,
        inventory_service,
        order_service,
        finance_service,
    ) -> None:
        self.supplier_service = supplier_service
        self.inventory_service = inventory_service
        self.order_service = order_service
        self.finance_service = finance_service
    # Input prompt helpers with validation
    def _prompt_text(self, prompt, default=None, required=True, min_length=1, max_length=None):
        while True:
            value = input(prompt).strip()
            if value.lower() == "cancel":
                return None
            if value == "" and default is not None:
                return default
            if value == "" and required:
                print("This field is required. Type CANCEL to return.")
                continue
            if len(value) < min_length:
                print(f"Enter at least {min_length} characters. Type CANCEL to return.")
                continue
            if max_length is not None and len(value) > max_length:
                print(f"Enter no more than {max_length} characters. Type CANCEL to return.")
                continue
            return value

    def _prompt_name(self, prompt, default=None, required=True, min_length=2, max_length=50):
        while True:
            value = self._prompt_text(prompt, default=default, required=required)
            if value is None:
                return None
            if len(value) < min_length:
                print(f"Enter at least {min_length} characters. Type CANCEL to return.")
                continue
            if len(value) > max_length:
                print(f"Enter no more than {max_length} characters. Type CANCEL to return.")
                continue
            if not all(ch.isalpha() or ch.isspace() or ch in "- '" for ch in value):
                print("Names may only contain letters, spaces, hyphens, or apostrophes. Type CANCEL to return.")
                continue
            if value.strip() == "" or all(ch in "- '" for ch in value):
                print("Enter a valid name. Type CANCEL to return.")
                continue
            return value

    def _prompt_email(self, prompt, default=None, required=True, min_length=5, max_length=100):
        while True:
            value = self._prompt_text(prompt, default=default, required=required, min_length=min_length, max_length=max_length)
            if value is None:
                return None
            normalized = value.strip()
            if "@" not in normalized or "." not in normalized or normalized.count("@") != 1:
                print("Enter a valid email address. Type CANCEL to return.")
                continue
            local, domain = normalized.split("@", 1)
            if not local or not domain or "." not in domain:
                print("Enter a valid email address. Type CANCEL to return.")
                continue
            return normalized

    def _prompt_phone(self, prompt, default=None, required=True, min_digits=7, max_length=20):
        while True:
            value = self._prompt_text(prompt, default=default, required=required)
            if value is None:
                return None
            digits = [ch for ch in value if ch.isdigit()]
            if len(digits) < min_digits:
                print(f"Enter a valid phone number with at least {min_digits} digits. Type CANCEL to return.")
                continue
            if len(value) > max_length:
                print(f"Enter no more than {max_length} characters. Type CANCEL to return.")
                continue
            if any(ch not in "0123456789 +()-" for ch in value):
                print("Enter a valid phone number. Type CANCEL to return.")
                continue
            return value

    def _prompt_int(self, prompt, default=None, required=True, min_value=None):
        while True:
            value = input(prompt).strip()
            if value.lower() == "cancel":
                return None
            if value == "" and default is not None:
                return default
            if value == "" and not required:
                return None
            if value == "" and required:
                print("This field is required. Type CANCEL to return.")
                continue
            try:
                parsed = int(value)
            except ValueError:
                print("Enter a valid integer. Type CANCEL to return.")
                continue
            if min_value is not None and parsed < min_value:
                print(f"Enter a number greater than or equal to {min_value}.")
                continue
            return parsed

    def _prompt_float(self, prompt, default=None, required=True, min_value=None):
        while True:
            value = input(prompt).strip()
            if value.lower() == "cancel":
                return None
            if value == "" and default is not None:
                return default
            if value == "" and not required:
                return None
            if value == "" and required:
                print("This field is required. Type CANCEL to return.")
                continue
            try:
                parsed = float(value)
            except ValueError:
                print("Enter a valid number. Type CANCEL to return.")
                continue
            if min_value is not None and parsed < min_value:
                print(f"Enter a number greater than or equal to {min_value}.")
                continue
            return parsed

    def _prompt_lookup_supplier_id(self, prompt, default=None):
        while True:
            supplier_id = self._prompt_text(prompt, default=default, required=default is None)
            if supplier_id is None:
                return None
            if self.supplier_service.get_supplier_by_id(supplier_id) is not None:
                return supplier_id
            print("Supplier not found. Enter a valid Supplier ID or type CANCEL.")

    def _prompt_lookup_product_id(self, prompt, default=None):
        while True:
            product_id = self._prompt_text(prompt, default=default, required=default is None)
            if product_id is None:
                return None
            if self.inventory_service.get_product_by_id(product_id) is not None:
                return product_id
            print("Product not found. Enter a valid Product ID or type CANCEL.")

    def _prompt_lookup_order_id(self, prompt, order_type):
        while True:
            order_id = self._prompt_text(prompt)
            if order_id is None:
                return None
            if order_type == "customer":
                if self.order_service.get_customer_order_by_id(order_id) is not None:
                    return order_id
            else:
                if self.order_service.get_purchase_order_by_id(order_id) is not None:
                    return order_id
            print("Order not found. Enter a valid Order ID or type CANCEL.")

    # Generic menu runner for submenus
    def _run_menu(self, title, options):
        while True:
            print(f"\n=== {title} ===")
            for index, (label, _) in enumerate(options, start=1):
                print(f"{index}. {label}")

            choice = input("Select an option: ").strip()
            if not choice.isdigit():
                print("Invalid option. Please enter a number.")
                continue

            choice_index = int(choice)
            if choice_index < 1 or choice_index > len(options):
                print("Invalid option. Please choose a valid number.")
                continue

            _, action = options[choice_index - 1]
            if action is None:
                return
            action()

    # Table styling
    def _format_table(self, headers, rows):
        widths = [len(header) for header in headers]
        for row in rows:
            for index, cell in enumerate(row):
                widths[index] = max(widths[index], len(str(cell)))

        header_row = " | ".join(header.ljust(widths[i]) for i, header in enumerate(headers))
        separator = "-+-".join("-" * widths[i] for i in range(len(headers)))

        print(header_row)
        print(separator)
        for row in rows:
            print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))

    # Print order in table layout.
    def _print_order(self, order):
        print(f"Order ID: {order.order_id} | Status: {order.status.value.capitalize()} | Created: {order.created_at:%Y-%m-%d %H:%M}")
        if order.order_type() == "customer":
            print(f"Customer: {getattr(order, 'customer_name', '')} <{getattr(order, 'customer_email', '')}>")
        else:
            print(f"Supplier ID: {getattr(order, 'supplier_id', '')}")

        lines = []
        for line in order.lines:
            lines.append([
                line.product_id,
                line.quantity,
                f"£{line.unit_price:.2f}",
                f"£{line.line_total():.2f}",
            ])
        self._format_table(["Product ID", "Qty", "Unit Price", "Line Total"], lines)
        print(f"Total Amount: £{order.total_amount():.2f}")
        print()

    # Main menu
    def run(self) -> None:
        options = [
            ("Customers", self._run_customers_menu),
            ("Orders", self._run_orders_menu),
            ("Suppliers", self._run_suppliers_menu),
            ("Finances", self._run_finances_menu),
            ("Inventory", self._run_inventory_menu),
            ("Exit", None),
        ]

        while True:
            print("\n=== BNU INDUSTRY SOLUTIONS WMS ===")
            for index, (label, _) in enumerate(options, start=1):
                print(f"{index}. {label}")

            choice = input("Select a category: ").strip()
            if not choice.isdigit():
                print("Invalid option. Please enter a number.")
                continue

            choice_index = int(choice)
            if choice_index < 1 or choice_index > len(options):
                print("Invalid option. Please choose a category from 1 to 6.")
                continue

            _, action = options[choice_index - 1]
            if action is None:
                print("Exiting system...")
                break
            action()

    # Customer-related actions menu.
    def _run_customers_menu(self) -> None:
        self._run_menu(
            "CUSTOMERS",
            [
                ("Create Customer Order", self.create_customer_order),
                ("View Customer Orders", self.view_customer_orders),
                ("Search Customer Order", self.search_customer_order),
                ("Update Customer Order", self.update_customer_order),
                ("Delete Customer Order", self.delete_customer_order),
                ("Back", None),
            ],
        )

    # Purchase order workflow menu.
    def _run_orders_menu(self) -> None:
        self._run_menu(
            "ORDERS",
            [
                ("Create Purchase Order", self.create_purchase_order),
                ("View Purchase Orders", self.view_purchase_orders),
                ("Search Purchase Order", self.search_purchase_order),
                ("Update Purchase Order", self.update_purchase_order),
                ("Delete Purchase Order", self.delete_purchase_order),
                ("Mark Purchase Order as Shipped", self.mark_purchase_order_as_shipped),
                ("Receive Purchase Order", self.receive_purchase_order),
                ("Back", None),
            ],
        )

    # Supplier management menu.
    def _run_suppliers_menu(self) -> None:
        self._run_menu(
            "SUPPLIERS",
            [
                ("View Suppliers", self.view_suppliers),
                ("Add Supplier", self.add_supplier),
                ("Update Supplier", self.update_supplier),
                ("Deactivate Supplier", self.deactivate_supplier),
                ("Back", None),
            ],
        )

    # Financial reporting menu.
    def _run_finances_menu(self) -> None:
        self._run_menu(
            "FINANCES",
            [
                ("View Financial Summary", self.view_financial_summary),
                ("View Financial Transactions", self.view_financial_transactions),
                ("View Sales Transactions", self.view_sales_transactions),
                ("View Expense Transactions", self.view_expense_transactions),
                ("Back", None),
            ],
        )

    # NOTE: Inventory management menu.
    def _run_inventory_menu(self) -> None:
        self._run_menu(
            "INVENTORY",
            [
                ("View Products", self.view_products),
                ("View Low Stock Alerts", self.view_low_stock),
                ("Add Product", self.add_product),
                ("Update Product", self.update_product),
                ("Delete Product", self.delete_product),
                ("Receive Stock", self.receive_stock),
                ("Back", None),
            ],
        )

    # Prints list of active suppliers
    def view_suppliers(self) -> None:
        print("\n=== SUPPLIERS ===")
        suppliers = self.supplier_service.list_active_suppliers()
        if not suppliers:
            print("No suppliers found.")
            return

        rows = []
        for supplier in suppliers:
            rows.append([
                supplier.supplier_id,
                supplier.name,
                supplier.contact_name,
                supplier.email,
                supplier.phone,
                supplier.address,
            ])
        self._format_table([
            "ID",
            "Name",
            "Contact",
            "Email",
            "Phone",
            "Address",
        ], rows)

    # Lists products
    def view_products(self) -> None:
        print("\n=== PRODUCTS ===")
        products = self.inventory_service.list_products()
        if not products:
            print("No products found.")
            return

        rows = []
        for product in products:
            rows.append([
                product.product_id,
                product.name,
                product.description,
                f"£{product.unit_price:.2f}",
                product.stock_quantity,
                product.reorder_level,
                product.supplier_id,
            ])
        self._format_table([
            "ID",
            "Name",
            "Description",
            "Price",
            "Stock",
            "Reorder",
            "Supplier",
        ], rows)

    # Only shows products below reorder level
    def view_low_stock(self) -> None:
        print("\n=== LOW STOCK ALERTS ===")
        products = self.inventory_service.low_stock_products()

        if not products:
            print("No low stock products.")
            return

        rows = []
        for product in products:
            rows.append([
                product.product_id,
                product.name,
                product.stock_quantity,
                product.reorder_level,
                product.supplier_id,
            ])
        self._format_table([
            "ID",
            "Name",
            "Stock",
            "Reorder",
            "Supplier",
        ], rows)

    # Pull totals from finance service
    def view_financial_summary(self) -> None:
        print("\n=== FINANCIAL SUMMARY ===")
        total_sales = self.finance_service.total_sales()
        total_expenses = self.finance_service.total_expenses()
        profit = self.finance_service.profit()

        print(f"Total Sales: £{total_sales:.2f}")
        print(f"Total Expenses: £{total_expenses:.2f}")
        print(f"Profit: £{profit:.2f}")

    # Creates a new supplier and lets the service generate the ID
    def add_supplier(self) -> None:
        print("\n=== ADD SUPPLIER ===")
        while True:
            name = self._prompt_name("Name: ")
            if name is None:
                return
            contact_name = self._prompt_name("Contact Name: ")
            if contact_name is None:
                return
            email = self._prompt_email("Email: ")
            if email is None:
                return
            phone = self._prompt_phone("Phone: ")
            if phone is None:
                return
            address = self._prompt_text("Address: ", min_length=5, max_length=100)
            if address is None:
                return

            supplier = self.supplier_service.add_supplier(
                name=name,
                contact_name=contact_name,
                email=email,
                phone=phone,
                address=address,
            )
            print(f"Supplier created with ID: {supplier.supplier_id}")
            return

    # Update supplier details
    def update_supplier(self) -> None:
        print("\n=== UPDATE SUPPLIER ===")
        while True:
            supplier_id = self._prompt_lookup_supplier_id("Supplier ID: ")
            if supplier_id is None:
                return

            supplier = self.supplier_service.get_supplier_by_id(supplier_id)
            if supplier is None:
                continue

            name = self._prompt_name(f"Name [{supplier.name}]: ", default=supplier.name)
            if name is None:
                return
            contact_name = self._prompt_name(
                f"Contact Name [{supplier.contact_name}]: ",
                default=supplier.contact_name,
            )
            if contact_name is None:
                return
            email = self._prompt_email(f"Email [{supplier.email}]: ", default=supplier.email)
            if email is None:
                return
            phone = self._prompt_phone(f"Phone [{supplier.phone}]: ", default=supplier.phone)
            if phone is None:
                return
            address = self._prompt_text(
                f"Address [{supplier.address}]: ",
                default=supplier.address,
                min_length=5,
                max_length=100,
            )
            if address is None:
                return

            try:
                self.supplier_service.update_supplier(
                    supplier_id=supplier_id,
                    name=name,
                    contact_name=contact_name,
                    email=email,
                    phone=phone,
                    address=address,
                )
                print("Supplier updated successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    # Deactivate a supplier by ID
    def deactivate_supplier(self) -> None:
        print("\n=== DEACTIVATE SUPPLIER ===")
        while True:
            supplier_id = self._prompt_lookup_supplier_id("Supplier ID: ")
            if supplier_id is None:
                return

            try:
                self.supplier_service.deactivate_supplier(supplier_id)
                print("Supplier deactivated successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    # Creates a new product and lets the service generate the ID
    def add_product(self) -> None:
        print("\n=== ADD PRODUCT ===")
        while True:
            name = self._prompt_text("Name: ")
            if name is None:
                return
            description = self._prompt_text("Description: ")
            if description is None:
                return
            supplier_id = self._prompt_lookup_supplier_id("Supplier ID: ")
            if supplier_id is None:
                return
            unit_price = self._prompt_float("Unit Price: ", min_value=0.0)
            if unit_price is None:
                return
            stock_quantity = self._prompt_int("Stock Quantity: ", min_value=0)
            if stock_quantity is None:
                return
            reorder_level = self._prompt_int("Reorder Level: ", min_value=0)
            if reorder_level is None:
                return

            product = self.inventory_service.add_product(
                name=name,
                description=description,
                unit_price=unit_price,
                stock_quantity=stock_quantity,
                reorder_level=reorder_level,
                supplier_id=supplier_id,
            )
            print(f"Product created with ID: {product.product_id}")
            return

    # Update product details
    def update_product(self) -> None:
        print("\n=== UPDATE PRODUCT ===")
        while True:
            product_id = self._prompt_lookup_product_id("Product ID: ")
            if product_id is None:
                return

            product = self.inventory_service.get_product_by_id(product_id)
            if product is None:
                continue

            name = self._prompt_text(f"Name [{product.name}]: ", default=product.name)
            if name is None:
                return
            description = self._prompt_text(
                f"Description [{product.description}]: ",
                default=product.description,
            )
            if description is None:
                return

            unit_price = self._prompt_float(
                f"Unit Price [{product.unit_price}]: ",
                default=product.unit_price,
                min_value=0.0,
            )
            if unit_price is None:
                return
            reorder_level = self._prompt_int(
                f"Reorder Level [{product.reorder_level}]: ",
                default=product.reorder_level,
                min_value=0,
            )
            if reorder_level is None:
                return

            supplier_id = self._prompt_lookup_supplier_id(
                f"Supplier ID [{product.supplier_id}]: ",
                default=product.supplier_id,
            )
            if supplier_id is None:
                return

            try:
                self.inventory_service.update_product(
                    product_id=product.product_id,
                    name=name,
                    description=description,
                    unit_price=unit_price,
                    reorder_level=reorder_level,
                    supplier_id=supplier_id,
                )
                print("Product updated successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    # Deletes a product from inventory
    def delete_product(self) -> None:
        print("\n=== DELETE PRODUCT ===")
        while True:
            product_id = self._prompt_lookup_product_id("Product ID: ")
            if product_id is None:
                return

            try:
                self.inventory_service.delete_product(product_id)
                print("Product deleted successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    # Increases stock for an existing product
    def receive_stock(self) -> None:
        print("\n=== RECEIVE STOCK ===")
        while True:
            product_id = self._prompt_lookup_product_id("Product ID: ")
            if product_id is None:
                return

            quantity = self._prompt_int("Quantity: ", min_value=1)
            if quantity is None:
                return

            try:
                self.inventory_service.receive_stock(product_id, quantity)
                print("Stock updated successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    # Creates a customer order; this is where stock gets reduced
    def create_customer_order(self) -> None:
        print("\n=== CREATE CUSTOMER ORDER ===")
        while True:
            customer_name = self._prompt_name("Customer Name: ")
            if customer_name is None:
                return
            customer_email = self._prompt_email("Customer Email: ")
            if customer_email is None:
                return

            product_id = self._prompt_lookup_product_id("Product ID: ")
            if product_id is None:
                return

            product = self.inventory_service.get_product_by_id(product_id)
            if product is None:
                print("Product not found.")
                continue

            while True:
                quantity = self._prompt_int("Quantity: ", min_value=1)
                if quantity is None:
                    return
                if quantity > product.stock_quantity:
                    print(
                        f"Only {product.stock_quantity} units are available. Enter a smaller quantity or type CANCEL."
                    )
                    continue
                break

            order_line = OrderLine(
                product_id=product.product_id,
                quantity=quantity,
                unit_price=product.unit_price,
            )

            try:
                order = self.order_service.create_customer_order(
                    customer_name=customer_name,
                    customer_email=customer_email,
                    lines=[order_line],
                )
                print(f"Customer order created with ID: {order.order_id}")
                print("Stock reduced successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")
        # Shows all customer orders currently stored in the system
    def view_customer_orders(self) -> None:
        print("\n=== CUSTOMER ORDERS ===")
        customer_orders = self.order_service.list_customer_orders()

        if not customer_orders:
            print("No customer orders found.")
            return

        for order in customer_orders:
            self._print_order(order)

    # Shows all purchase orders currently stored in the system
    def view_purchase_orders(self) -> None:
        print("\n=== PURCHASE ORDERS ===")
        purchase_orders = self.order_service.list_purchase_orders()

        if not purchase_orders:
            print("No purchase orders found.")
            return

        for order in purchase_orders:
            self._print_order(order)

    # Find and show a single customer order by ID
    def search_customer_order(self) -> None:
        print("\n=== SEARCH CUSTOMER ORDER ===")
        while True:
            order_id = self._prompt_lookup_order_id("Customer Order ID: ", order_type="customer")
            if order_id is None:
                return
            order = self.order_service.get_customer_order_by_id(order_id)
            if order is None:
                continue
            print(order)
            return

    # Find and show a single purchase order by ID
    def search_purchase_order(self) -> None:
        print("=== SEARCH PURCHASE ORDER ===")
        while True:
            order_id = self._prompt_lookup_order_id("Purchase Order ID: ", order_type="purchase")
            if order_id is None:
                return
            order = self.order_service.get_purchase_order_by_id(order_id)
            if order is None:
                continue
            print(order)
            return

    # Shows every recorded financial transaction
    def view_financial_transactions(self) -> None:
        print("\n=== FINANCIAL TRANSACTIONS ===")
        transactions = self.finance_service.get_all_transactions()

        if not transactions:
            print("No financial transactions found.")
            return

        rows = []
        for transaction in transactions:
            rows.append([
                transaction.created_at.date(),
                transaction.transaction_type().value.upper(),
                f"£{transaction.amount:.2f}",
                transaction.description,
            ])
        self._format_table(["Date", "Type", "Amount", "Description"], rows)

    # Shows only sales transactions
    def view_sales_transactions(self) -> None:
        print("=== SALES TRANSACTIONS ===")
        transactions = self.finance_service.get_sales_transactions()

        if not transactions:
            print("No sales transactions found.")
            return

        rows = []
        for transaction in transactions:
            rows.append([
                transaction.created_at.date(),
                transaction.transaction_type().value.upper(),
                f"£{transaction.amount:.2f}",
                transaction.description,
            ])
        self._format_table(["Date", "Type", "Amount", "Description"], rows)

    # Shows only expense transactions
    def view_expense_transactions(self) -> None:
        print("=== EXPENSE TRANSACTIONS ===")
        transactions = self.finance_service.get_expense_transactions()

        if not transactions:
            print("No expense transactions found.")
            return

        rows = []
        for transaction in transactions:
            rows.append([
                transaction.created_at.date(),
                transaction.transaction_type().value.upper(),
                f"£{transaction.amount:.2f}",
                transaction.description,
            ])
        self._format_table(["Date", "Type", "Amount", "Description"], rows)
    
    def create_purchase_order(self) -> None:
        print("\n=== CREATE PURCHASE ORDER ===")
        while True:
            supplier_id = self._prompt_lookup_supplier_id("Supplier ID: ")
            if supplier_id is None:
                return
            product_id = self._prompt_lookup_product_id("Product ID: ")
            if product_id is None:
                return

            quantity = self._prompt_int("Quantity: ", min_value=1)
            if quantity is None:
                return

            product = self.inventory_service.get_product_by_id(product_id)
            if product is None:
                print("Product not found.")
                continue

            order_line = OrderLine(
                product_id=product.product_id,
                quantity=quantity,
                unit_price=product.unit_price,
            )

            try:
                order = self.order_service.create_purchase_order(
                    supplier_id=supplier_id,
                    lines=[order_line],
                )
                print(f"Purchase order created with ID: {order.order_id}")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")
    
    def mark_purchase_order_as_shipped(self) -> None:
        print("\n=== MARK PURCHASE ORDER AS SHIPPED ===")
        while True:
            order_id = self._prompt_lookup_order_id("Purchase Order ID: ", order_type="purchase")
            if order_id is None:
                return

            try:
                self.order_service.mark_purchase_order_as_shipped(order_id)
                print("Purchase order marked as shipped.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    def receive_purchase_order(self) -> None:
        print("=== RECEIVE PURCHASE ORDER ===")
        while True:
            order_id = self._prompt_lookup_order_id("Purchase Order ID: ", order_type="purchase")
            if order_id is None:
                return

            try:
                self.order_service.receive_purchase_order(order_id)
                print("Purchase order marked as delivered and stock updated.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    # Update an existing pending customer order
    def update_customer_order(self) -> None:
        print("\n=== UPDATE CUSTOMER ORDER ===")
        while True:
            order_id = self._prompt_lookup_order_id("Customer Order ID: ", order_type="customer")
            if order_id is None:
                return

            order = self.order_service.get_customer_order_by_id(order_id)
            if order is None:
                continue

            customer_name = self._prompt_name(
                f"Customer Name [{order.customer_name}]: ",
                default=order.customer_name,
            )
            if customer_name is None:
                return
            customer_email = self._prompt_email(
                f"Customer Email [{order.customer_email}]: ",
                default=order.customer_email,
            )
            if customer_email is None:
                return

            update_lines = input("Update order lines? (y/N): ").strip().lower() == "y"
            lines = None
            if update_lines:
                product_id = self._prompt_lookup_product_id("Product ID: ")
                if product_id is None:
                    return

                product = self.inventory_service.get_product_by_id(product_id)
                if product is None:
                    print("Product not found.")
                    continue

                existing_quantity = 0
                for line in order.lines:
                    if line.product_id == product_id:
                        existing_quantity += line.quantity

                available_stock = product.stock_quantity + existing_quantity
                while True:
                    quantity = self._prompt_int("Quantity: ", min_value=1)
                    if quantity is None:
                        return
                    if quantity > available_stock:
                        print(
                            f"Only {available_stock} total units are available for this product. Enter a smaller quantity or type CANCEL."
                        )
                        continue
                    break

                lines = [
                    OrderLine(
                        product_id=product.product_id,
                        quantity=quantity,
                        unit_price=product.unit_price,
                    )
                ]

            try:
                self.order_service.update_customer_order(
                    order_id=order_id,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    lines=lines,
                )
                print("Customer order updated successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    # Update an existing pending purchase order
    def update_purchase_order(self) -> None:
        print("\n=== UPDATE PURCHASE ORDER ===")
        while True:
            order_id = self._prompt_lookup_order_id("Purchase Order ID: ", order_type="purchase")
            if order_id is None:
                return

            order = self.order_service.get_purchase_order_by_id(order_id)
            if order is None:
                continue

            supplier_id = self._prompt_lookup_supplier_id(
                f"Supplier ID [{order.supplier_id}]: ",
                default=order.supplier_id,
            )
            if supplier_id is None:
                return

            update_lines = input("Update order lines? (y/N): ").strip().lower() == "y"
            lines = None
            if update_lines:
                product_id = self._prompt_lookup_product_id("Product ID: ")
                if product_id is None:
                    return

                product = self.inventory_service.get_product_by_id(product_id)
                if product is None:
                    print("Product not found.")
                    continue

                quantity = self._prompt_int("Quantity: ", min_value=1)
                if quantity is None:
                    return

                lines = [
                    OrderLine(
                        product_id=product.product_id,
                        quantity=quantity,
                        unit_price=product.unit_price,
                    )
                ]

            try:
                self.order_service.update_purchase_order(
                    order_id=order_id,
                    supplier_id=supplier_id,
                    lines=lines,
                )
                print("Purchase order updated successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    # Delete an existing pending customer order
    def delete_customer_order(self) -> None:
        print("\n=== DELETE CUSTOMER ORDER ===")
        while True:
            order_id = self._prompt_lookup_order_id("Customer Order ID: ", order_type="customer")
            if order_id is None:
                return

            try:
                self.order_service.delete_customer_order(order_id)
                print("Customer order deleted successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")

    # Delete an existing pending purchase order
    def delete_purchase_order(self) -> None:
        print("\n=== DELETE PURCHASE ORDER ===")
        while True:
            order_id = self._prompt_lookup_order_id("Purchase Order ID: ", order_type="purchase")
            if order_id is None:
                return

            try:
                self.order_service.delete_purchase_order(order_id)
                print("Purchase order deleted successfully.")
                return
            except ValueError as error:
                print(f"Error: {error}")
                print("Try again or type CANCEL to return.")