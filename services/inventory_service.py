from models.bnu_models import Product


class InventoryService:
    def __init__(self) -> None:
        self._products: list[Product] = []

    # Adds new product to inventory with a unique product ID
    def add_product(self, product: Product) -> None:
        if self.get_product_by_id(product.product_id) is not None:
            raise ValueError("Product ID already exists.")
        self._products.append(product)

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

    # Stock quantity reduces when dispatched
    def low_stock_products(self) -> list[Product]:
        return [product for product in self._products if product.is_low_stock()]