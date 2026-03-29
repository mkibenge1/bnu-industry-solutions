from models.bnu_models import Product, Supplier
from services.inventory_service import InventoryService
from services.supplier_service import SupplierService


def main() -> None:
    supplier_service = SupplierService()
    inventory_service = InventoryService()
    
    # Added test suppliers
    supplier_1 = Supplier(
        supplier_id="S001",
        name="Midlands Industrial Supplies Ltd",
        contact_name="Sarah Bennett",
        email="sarah.bennett@midlandsindustrial.co.uk",
        phone="01494 555321",
        address="Unit 4, Cressex Business Park, High Wycombe, HP12 3RL",
    )

    supplier_2 = Supplier(
        supplier_id="S002",
        name="Thames Valley Safety Equipment Ltd",
        contact_name="Michael Turner",
        email="m.turner@tvse.co.uk",
        phone="01628 442210",
        address="18 Trading Estate Road, Slough, SL1 4AB",
    )

    supplier_service.add_supplier(supplier_1)
    supplier_service.add_supplier(supplier_2)

    # Added test products to inventory
    product_1 = Product(
        product_id="P001",
        name="Industrial Hammer",
        description="Heavy-duty steel claw hammer for construction and maintenance work",
        unit_price=12.99,
        stock_quantity=50,
        reorder_level=10,
        supplier_id="S001",
    )

    # Added a product with low stock to test low stock alerts
    product_2 = Product(
        product_id="P002",
        name="Safety Gloves Pack",
        description="Pack of 10 reinforced protective gloves for warehouse handling",
        unit_price=8.50,
        stock_quantity=6,
        reorder_level=10,
        supplier_id="S002",
    )

    product_3 = Product(
        product_id="P003",
        name="Adjustable Spanner",
        description="250mm adjustable steel spanner for industrial repair tasks",
        unit_price=15.75,
        stock_quantity=22,
        reorder_level=5,
        supplier_id="S001",
    )

    inventory_service.add_product(product_1)
    inventory_service.add_product(product_2)
    inventory_service.add_product(product_3)

    inventory_service.receive_stock("P001", 20)

    # list active suppliers
    print("=== ACTIVE SUPPLIERS ===")
    for current_supplier in supplier_service.list_active_suppliers():
        print(current_supplier)

    # List inventory
    print("\n=== CURRENT INVENTORY ===")
    for current_product in inventory_service.list_products():
        print(current_product)

    # Low stock products listed
    print("\n=== LOW STOCK ALERTS ===")
    low_stock_products = inventory_service.low_stock_products()
    if not low_stock_products:
        print("No low stock products found.")
    else:
        for low_stock_product in low_stock_products:
            print(low_stock_product)


if __name__ == "__main__":
    main()