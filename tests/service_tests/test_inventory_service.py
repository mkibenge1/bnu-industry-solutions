import unittest
from unittest.mock import Mock, patch

from models.bnu_models import Product
from services.inventory_service import InventoryService


class TestInventoryService(unittest.TestCase):
# test for add update receive and delete product
    @patch("services.inventory_service.ProductRepository")
    # test for add update receive and delete product
    def test_add_update_receive_and_delete_product(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = InventoryService()

        product = service.add_product(
            name="Widget",
            description="Standard widget",
            unit_price=2.0,
            stock_quantity=10,
            reorder_level=3,
            supplier_id="S001",
        )

        self.assertEqual(product.name, "Widget")
        self.assertEqual(product.product_id, "P001")
        self.assertEqual(len(service.list_products()), 1)

        service.receive_stock("P001", 5)
        self.assertEqual(product.stock_quantity, 15)

        service.update_product(
            product_id="P001",
            name="Widget Pro",
            description="Updated widget",
            unit_price=2.5,
            reorder_level=2,
            supplier_id="S001",
        )
        self.assertEqual(service.get_product_by_id("P001").name, "Widget Pro")

        service.delete_product("P001")
        self.assertEqual(service.list_products(), [])

# test for low stock products
    @patch("services.inventory_service.ProductRepository")
    # test for low stock products
    def test_low_stock_products(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = InventoryService()
        product_a = service.add_product(
            name="Widget A",
            description="A widget",
            unit_price=3.0,
            stock_quantity=2,
            reorder_level=5,
            supplier_id="S001",
        )
        product_b = service.add_product(
            name="Widget B",
            description="Another widget",
            unit_price=4.0,
            stock_quantity=10,
            reorder_level=5,
            supplier_id="S001",
        )

        low_stock = service.low_stock_products()
        self.assertEqual(len(low_stock), 1)
        self.assertEqual(low_stock[0].product_id, product_a.product_id)

# test for update product raises when product missing
    @patch("services.inventory_service.ProductRepository")
    # test for update product raises when product missing
    def test_update_product_raises_when_product_missing(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = InventoryService()
        with self.assertRaises(ValueError):
            service.update_product(
                product_id="P999",
                name="Missing",
                description="Missing product",
                unit_price=1.0,
                reorder_level=1,
                supplier_id="S001",
            )

# test for get product by id returns none when missing
    @patch("services.inventory_service.ProductRepository")
    # test for get product by id returns none when missing
    def test_get_product_by_id_returns_none_when_missing(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = InventoryService()
        self.assertIsNone(service.get_product_by_id("P999"))

# test for add product id does not reuse deleted ids
    @patch("services.inventory_service.ProductRepository")
    # test for add product does not reuse deleted id
    def test_add_product_does_not_reuse_deleted_id(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = InventoryService()
        first = service.add_product("Widget A", "A", 1.0, 1, 1, "S001")
        second = service.add_product("Widget B", "B", 1.0, 1, 1, "S001")
        service.delete_product(first.product_id)
        third = service.add_product("Widget C", "C", 1.0, 1, 1, "S001")

        self.assertEqual(second.product_id, "P002")
        self.assertEqual(third.product_id, "P003")


if __name__ == "__main__":
    unittest.main()
