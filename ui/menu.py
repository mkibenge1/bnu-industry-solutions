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
            print("9. Exit")
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