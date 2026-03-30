from models.bnu_models import Product

class InventoryService:
    def __init__(self) -> None:
        self._products: list[Product] = []

    # Generates unique ID
    def _generate_product_id(self) -> str:
        return f"P{len(self._products) + 1:03}"

    # Adds a new product to inventory and automatically assigns an ID
    def add_product(
        self,
        name: str,
        description: str,
        unit_price: float,
        stock_quantity: int,
        reorder_level: int,
        supplier_id: str,
    ) -> Product:
        product = Product(
            product_id=self._generate_product_id(),
            name=name,
            description=description,
            unit_price=unit_price,
            stock_quantity=stock_quantity,
            reorder_level=reorder_level,
            supplier_id=supplier_id,
        )
        self._products.append(product)
        return product

    # Retrieves a product by its unique ID, returns None if not found
    def get_product_by_id(self, product_id: str) -> Product | None:
        for product in self._products:
            if product.product_id == product_id:
                return product
        return None

    # Returns a list of all products currently in inventory
    def list_products(self) -> list[Product]:
        return self._products.copy()

    # Updates product details based on provided info
    def update_product(
        self,
        product_id: str,
        name: str,
        description: str,
        unit_price: float,
        reorder_level: int,
        supplier_id: str,
    ) -> None:
        product = self.get_product_by_id(product_id)
        if product is None:
            raise ValueError("Product not found.")

        product.name = name
        product.description = description
        product.unit_price = unit_price
        product.reorder_level = reorder_level
        product.supplier_id = supplier_id

    # Stock quantity increases when received
    def receive_stock(self, product_id: str, quantity: int) -> None:
        product = self.get_product_by_id(product_id)
        if product is None:
            raise ValueError("Product not found.")
        product.increase_stock(quantity)

    # Returns all products that are at or below their reorder level
    def low_stock_products(self) -> list[Product]:
        return [product for product in self._products if product.is_low_stock()]