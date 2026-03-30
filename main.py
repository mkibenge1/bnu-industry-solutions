from services.finance_service import FinanceService
from services.inventory_service import InventoryService
from services.order_service import OrderService
from services.supplier_service import SupplierService
from ui.menu import Menu

# Add test data for demo purposes
def add_data(
    supplier_service: SupplierService,
    inventory_service: InventoryService,
) -> None:
    # Create suppliers
    supplier_1 = supplier_service.add_supplier(
        name="Midlands Industrial Supplies Ltd",
        contact_name="Sarah Bennett",
        email="sarah.bennett@midlandsindustrial.co.uk",
        phone="01494 555321",
        address="High Wycombe",
    )

    supplier_2 = supplier_service.add_supplier(
        name="Thames Valley Safety Equipment Ltd",
        contact_name="Michael Turner",
        email="m.turner@tvse.co.uk",
        phone="01628 442210",
        address="Slough",
    )

    # Create products linked to suppliers
    inventory_service.add_product(
        name="Industrial Hammer",
        description="Heavy-duty hammer",
        unit_price=12.99,
        stock_quantity=50,
        reorder_level=10,
        supplier_id=supplier_1.supplier_id,
    )

    inventory_service.add_product(
        name="Safety Gloves Pack",
        description="Pack of 10 reinforced gloves",
        unit_price=8.50,
        stock_quantity=6,
        reorder_level=10,
        supplier_id=supplier_2.supplier_id,
    )

    inventory_service.add_product(
        name="Adjustable Spanner",
        description="Steel adjustable spanner",
        unit_price=15.75,
        stock_quantity=22,
        reorder_level=5,
        supplier_id=supplier_1.supplier_id,
    )


def main() -> None:
    # Create service instances
    supplier_service = SupplierService()
    inventory_service = InventoryService()
    finance_service = FinanceService()
    order_service = OrderService(
        inventory_service,
        supplier_service,
        finance_service,
    )

    add_data(supplier_service, inventory_service)

    # Create menu
    menu = Menu(
        supplier_service,
        inventory_service,
        order_service,
        finance_service,
    )
    menu.run()


if __name__ == "__main__":
    main()