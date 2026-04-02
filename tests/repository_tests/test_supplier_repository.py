import json
import tempfile
import unittest
from pathlib import Path

from models.bnu_models import Supplier
from repositories.supplier_repository import SupplierRepository


class TestSupplierRepository(unittest.TestCase):
# test for save and load supplier
    def test_save_and_load_supplier(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "suppliers.json"
            repository = SupplierRepository(str(path))

            supplier = Supplier(
                supplier_id="S001",
                name="Acme Supplies",
                contact_name="Jane Doe",
                email="jane@acme.example",
                phone="07123456789",
                address="10 Industry Drive",
            )
            repository.save([supplier])

            loaded = repository.load()
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].supplier_id, "S001")
            self.assertEqual(loaded[0].name, "Acme Supplies")
            self.assertEqual(loaded[0].email, "jane@acme.example")

            self.assertTrue(path.exists())
            self.assertIn("Acme Supplies", path.read_text())

# test for load returns empty when file missing
    def test_load_returns_empty_when_file_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "suppliers.json"
            repository = SupplierRepository(str(path))
            self.assertEqual(repository.load(), [])

    # test for load raises when json is malformed
    def test_load_raises_when_json_is_malformed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "suppliers.json"
            path.write_text("[ { invalid json ]", encoding="utf-8")
            repository = SupplierRepository(str(path))
            with self.assertRaises(json.JSONDecodeError):
                repository.load()

    # test for load defaults is active when field missing
    def test_load_defaults_is_active_when_field_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "suppliers.json"
            data = [
                {
                    "supplier_id": "S001",
                    "name": "Acme Supplies",
                    "contact_name": "Jane Doe",
                    "email": "jane@acme.example",
                    "phone": "07123456789",
                    "address": "10 Industry Drive",
                }
            ]
            path.write_text(json.dumps(data), encoding="utf-8")

            repository = SupplierRepository(str(path))
            loaded = repository.load()
            self.assertEqual(len(loaded), 1)
            self.assertTrue(loaded[0].is_active)


if __name__ == "__main__":
    unittest.main()
