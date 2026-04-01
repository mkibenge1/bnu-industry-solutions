import json
from pathlib import Path

from models.bnu_models import Product


class ProductRepository:
    def __init__(self, file_path: str = "data/products.json") -> None:
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
    # Save products to JSON file
    def save(self, products: list[Product]) -> None:
        product_data = []

        for product in products:
            product_data.append(
                {
                    "product_id": product.product_id,
                    "name": product.name,
                    "description": product.description,
                    "unit_price": product.unit_price,
                    "stock_quantity": product.stock_quantity,
                    "reorder_level": product.reorder_level,
                    "supplier_id": product.supplier_id,
                }
            )

        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(product_data, file, indent=4)
    # Load products from JSON file
    def load(self) -> list[Product]:
        if not self._file_path.exists():
            return []
        with self._file_path.open("r", encoding="utf-8") as file:
            product_data = json.load(file)

        products: list[Product] = []

        for item in product_data:
            products.append(
                Product(
                    product_id=item["product_id"],
                    name=item["name"],
                    description=item["description"],
                    unit_price=item["unit_price"],
                    stock_quantity=item["stock_quantity"],
                    reorder_level=item["reorder_level"],
                    supplier_id=item["supplier_id"],
                )
            )

        return products