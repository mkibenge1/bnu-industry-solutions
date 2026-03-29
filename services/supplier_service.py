from models.bnu_models import Supplier


class SupplierService:
    def __init__(self) -> None:
        self._suppliers: list[Supplier] = []
    
    # Adds a new supplier with their own unique ID
    def add_supplier(self, supplier: Supplier) -> None:
        if self.get_supplier_by_id(supplier.supplier_id) is not None:
            raise ValueError("Supplier ID already exists.")
        self._suppliers.append(supplier)
    
    # Retrieves supplier info using their ID, otherwise returns none if not found
    def get_supplier_by_id(self, supplier_id: str) -> Supplier | None:
        for supplier in self._suppliers:
            if supplier.supplier_id == supplier_id:
                return supplier
        return None
    
    # Returns a list of all active suppliers
    def list_active_suppliers(self) -> list[Supplier]:
        return [supplier for supplier in self._suppliers if supplier.is_active]
    
    # Updates supplier info
    def update_supplier(
        self,
        supplier_id: str,
        name: str,
        contact_name: str,
        email: str,
        phone: str,
        address: str,
    ) -> None:
        supplier = self.get_supplier_by_id(supplier_id)
        if supplier is None:
            raise ValueError("Supplier not found.")

        supplier.name = name
        supplier.contact_name = contact_name
        supplier.email = email
        supplier.phone = phone
        supplier.address = address

    # Deactivates a supplier, preventing future orders from them
    def deactivate_supplier(self, supplier_id: str) -> None:
        supplier = self.get_supplier_by_id(supplier_id)
        if supplier is None:
            raise ValueError("Supplier not found.")
        supplier.is_active = False