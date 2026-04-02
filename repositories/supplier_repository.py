import json
from pathlib import Path

from models.bnu_models import Supplier


# Store suppliers in a JSON file for reuse
class SupplierRepository:
    # Make sure the data folder exists
    def __init__(self, file_path: str = "data/suppliers.json") -> None:
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, suppliers: list[Supplier]) -> None:
        supplier_data = []

        # Convert each supplier into simple JSON
        for supplier in suppliers:
            supplier_data.append(
                {
                    "supplier_id": supplier.supplier_id,
                    "name": supplier.name,
                    "contact_name": supplier.contact_name,
                    "email": supplier.email,
                    "phone": supplier.phone,
                    "address": supplier.address,
                    "is_active": supplier.is_active,
                }
            )

        # Write file in readable JSON
        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(supplier_data, file, indent=4)

    # Load suppliers from the JSON file
    def load(self) -> list[Supplier]:
        if not self._file_path.exists():
            return []
        with self._file_path.open("r", encoding="utf-8") as file:
            supplier_data = json.load(file)

        suppliers: list[Supplier] = []

        # Rebuild supplier objects from stored values
        for item in supplier_data:
            suppliers.append(
                Supplier(
                    supplier_id=item["supplier_id"],
                    name=item["name"],
                    contact_name=item["contact_name"],
                    email=item["email"],
                    phone=item["phone"],
                    address=item["address"],
                    is_active=item.get("is_active", True),
                )
            )

        return suppliers