from services.finance_service import FinanceService
from services.inventory_service import InventoryService
from services.order_service import OrderService
from services.supplier_service import SupplierService
from ui.menu import Menu

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