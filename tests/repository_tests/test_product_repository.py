import json
import tempfile
import unittest
from pathlib import Path

from models.bnu_models import Product
from repositories.product_repository import ProductRepository


class TestProductRepository(unittest.TestCase):
# test for save and load product
    def test_save_and_load_product(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "products.json"
            repository = ProductRepository(str(path))

            product = Product(
                product_id="P001",
                name="Widget",
                description="A test widget",
                unit_price=5.0,
                stock_quantity=12,
                reorder_level=3,
                supplier_id="S001",
            )
            repository.save([product])

            loaded = repository.load()
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].product_id, "P001")
            self.assertEqual(loaded[0].name, "Widget")
            self.assertEqual(loaded[0].stock_quantity, 12)
            self.assertTrue(path.exists())

# test for load returns empty when file missing
    def test_load_returns_empty_when_file_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "products.json"
            repository = ProductRepository(str(path))
            self.assertEqual(repository.load(), [])

    # test for load raises when json is malformed
    def test_load_raises_when_json_is_malformed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "products.json"
            path.write_text("{ invalid json }", encoding="utf-8")
            repository = ProductRepository(str(path))
            with self.assertRaises(json.JSONDecodeError):
                repository.load()


if __name__ == "__main__":
    unittest.main()
