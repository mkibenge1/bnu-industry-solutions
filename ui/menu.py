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

    def run(self) -> None:
        # Creates text-based menu for user interaction
        while True:
            print("\n=== BNU INDUSTRY SOLUTIONS WMS ===")
            print("1. View Suppliers")
            print("2. View Products")
            print("3. View Low Stock Alerts")
            print("4. View Financial Summary")
            print("5. Add Supplier")
            print("6. Add Product")
            print("7. Receive Stock")
            print("8. Create Customer Order")
            print("9. Create Purchase Order")
            print("10. Mark Purchase Order as Shipped")
            print("11. Receive Purchase Order")
            print("12. View Customer Orders")
            print("13. View Purchase Orders")
            print("14. View Financial Transactions")
            print("15. Exit")

            choice = input("Select an option: ")

            # Route user choice to the correct function
            if choice == "1":
                self.view_suppliers()
            elif choice == "2":
                self.view_products()
            elif choice == "3":
                self.view_low_stock()
            elif choice == "4":
                self.view_financial_summary()
            elif choice == "5":
                self.add_supplier()
            elif choice == "6":
                self.add_product()
            elif choice == "7":
                self.receive_stock()
            elif choice == "8":
                self.create_customer_order()
            elif choice == "9":
                self.create_purchase_order()
            elif choice == "10":
                self.mark_purchase_order_as_shipped()
            elif choice == "11":
                self.receive_purchase_order()
            elif choice == "12":
                self.view_customer_orders()
            elif choice == "13":
                self.view_purchase_orders()
            elif choice == "14":
                self.view_financial_transactions()
            elif choice == "15":
                print("Exiting system...")
                break
            else:
                print("Invalid option.")

    # Prints list of active suppliers
    def view_suppliers(self) -> None:
        print("\n=== SUPPLIERS ===")
        suppliers = self.supplier_service.list_active_suppliers()
        if not suppliers:
            print("No suppliers found.")
        else:
            for supplier in suppliers:
                print(supplier)

    # Lists products
    def view_products(self) -> None:
        print("\n=== PRODUCTS ===")
        products = self.inventory_service.list_products()
        if not products:
            print("No products found.")
        else:
            for product in products:
                print(product)

    # Only shows products below reorder level
    def view_low_stock(self) -> None:
        print("\n=== LOW STOCK ALERTS ===")
        products = self.inventory_service.low_stock_products()

        if not products:
            print("No low stock products.")
        else:
            for product in products:
                print(product)

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
        name = input("Name: ")
        contact_name = input("Contact Name: ")
        email = input("Email: ")
        phone = input("Phone: ")
        address = input("Address: ")

        supplier = self.supplier_service.add_supplier(
            name=name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            address=address,
        )

        print(f"Supplier created with ID: {supplier.supplier_id}")

    # Creates a new product and lets the service generate the ID
    def add_product(self) -> None:
        print("\n=== ADD PRODUCT ===")
        name = input("Name: ")
        description = input("Description: ")
        supplier_id = input("Supplier ID: ")

        try:
            unit_price = float(input("Unit Price: "))
            stock_quantity = int(input("Stock Quantity: "))
            reorder_level = int(input("Reorder Level: "))
        except ValueError:
            print("Invalid number entered.")
            return

        if self.supplier_service.get_supplier_by_id(supplier_id) is None:
            print("Supplier not found.")
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

    # Increases stock for an existing product
    def receive_stock(self) -> None:
        print("\n=== RECEIVE STOCK ===")
        product_id = input("Product ID: ")

        try:
            quantity = int(input("Quantity: "))
            self.inventory_service.receive_stock(product_id, quantity)
            print("Stock updated successfully.")
        except ValueError as error:
            print(f"Error: {error}")

    # Creates a customer order; this is where stock gets reduced
    def create_customer_order(self) -> None:
        print("\n=== CREATE CUSTOMER ORDER ===")
        customer_name = input("Customer Name: ")
        customer_email = input("Customer Email: ")

        product_id = input("Product ID: ")

        try:
            quantity = int(input("Quantity: "))
        except ValueError:
            print("Invalid quantity entered.")
            return

        product = self.inventory_service.get_product_by_id(product_id)
        if product is None:
            print("Product not found.")
            return

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
        except ValueError as error:
            print(f"Error: {error}")
        # Shows all customer orders currently stored in the system
    def view_customer_orders(self) -> None:
        print("\n=== CUSTOMER ORDERS ===")
        customer_orders = self.order_service.list_customer_orders()

        if not customer_orders:
            print("No customer orders found.")
        else:
            for order in customer_orders:
                print(order)

    # Shows all purchase orders currently stored in the system
    def view_purchase_orders(self) -> None:
        print("\n=== PURCHASE ORDERS ===")
        purchase_orders = self.order_service.list_purchase_orders()

        if not purchase_orders:
            print("No purchase orders found.")
        else:
            for order in purchase_orders:
                print(order)

    # Shows every recorded financial transaction
    def view_financial_transactions(self) -> None:
        print("\n=== FINANCIAL TRANSACTIONS ===")
        transactions = self.finance_service.get_all_transactions()

        if not transactions:
            print("No financial transactions found.")
        else:
            for transaction in transactions:
                print(transaction.to_report_row())
    
    def create_purchase_order(self) -> None:
        print("\n=== CREATE PURCHASE ORDER ===")
        supplier_id = input("Supplier ID: ")
        product_id = input("Product ID: ")

        try:
            quantity = int(input("Quantity: "))
        except ValueError:
            print("Invalid quantity entered.")
            return

        product = self.inventory_service.get_product_by_id(product_id)
        if product is None:
            print("Product not found.")
            return

        supplier = self.supplier_service.get_supplier_by_id(supplier_id)
        if supplier is None:
            print("Supplier not found.")
            return

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
        except ValueError as error:
            print(f"Error: {error}")
    
    def mark_purchase_order_as_shipped(self) -> None:
        print("\n=== MARK PURCHASE ORDER AS SHIPPED ===")
        order_id = input("Purchase Order ID: ")
        try:
            self.order_service.mark_purchase_order_as_shipped(order_id)
            print("Purchase order marked as shipped.")
        except ValueError as error:
            print(f"Error: {error}")

    def receive_purchase_order(self) -> None:
        print("\n=== RECEIVE PURCHASE ORDER ===")
        order_id = input("Purchase Order ID: ")

        try:
            self.order_service.receive_purchase_order(order_id)
            print("Purchase order marked as delivered and stock updated.")
        except ValueError as error:
            print(f"Error: {error}")