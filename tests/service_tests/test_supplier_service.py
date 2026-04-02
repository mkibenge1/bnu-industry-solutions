import unittest
from unittest.mock import Mock, patch

from services.supplier_service import SupplierService


class TestSupplierService(unittest.TestCase):
# test for add update and delete supplier
    @patch("services.supplier_service.SupplierRepository")
    # test for add update and delete supplier
    def test_add_update_and_delete_supplier(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = SupplierService()

        supplier = service.add_supplier(
            name="Acme Supplies",
            contact_name="Jane Doe",
            email="jane@acme.example",
            phone="07123456789",
            address="10 Industry Drive",
        )

        self.assertEqual(supplier.supplier_id, "S001")
        self.assertEqual(service.get_supplier_by_id("S001"), supplier)
        self.assertEqual(len(service.list_active_suppliers()), 1)
        self.assertTrue(service.list_active_suppliers()[0].is_active)

        service.update_supplier(
            supplier_id="S001",
            name="Acme Supplies Ltd",
            contact_name="Jane Doe",
            email="jane.doe@acme.example",
            phone="07123456789",
            address="10 Industry Drive",
        )
        self.assertEqual(service.get_supplier_by_id("S001").email, "jane.doe@acme.example")

        service.delete_supplier("S001")
        self.assertIsNone(service.get_supplier_by_id("S001"))

# test for get supplier by id returns none when missing
    @patch("services.supplier_service.SupplierRepository")
    # test for get supplier by id returns none when missing
    def test_get_supplier_by_id_returns_none_when_missing(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = SupplierService()
        self.assertIsNone(service.get_supplier_by_id("S999"))

# test for update supplier raises when missing
    @patch("services.supplier_service.SupplierRepository")
    # test for update supplier raises when missing
    def test_update_supplier_raises_when_missing(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = SupplierService()
        with self.assertRaises(ValueError):
            service.update_supplier(
                supplier_id="S999",
                name="Missing",
                contact_name="Nobody",
                email="none@example.com",
                phone="0000000000",
                address="Nowhere",
            )

# test for delete supplier raises when missing
    @patch("services.supplier_service.SupplierRepository")
    # test for delete supplier raises when missing
    def test_delete_supplier_raises_when_missing(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = SupplierService()
        with self.assertRaises(ValueError):
            service.delete_supplier("S999")

# test for add supplier id does not reuse deleted ids
    @patch("services.supplier_service.SupplierRepository")
    # test for add supplier does not reuse deleted id
    def test_add_supplier_does_not_reuse_deleted_id(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.load.return_value = []
        mock_repo.save = Mock()

        service = SupplierService()
        first = service.add_supplier("A", "A", "a@example.com", "07111111111", "Addr A")
        second = service.add_supplier("B", "B", "b@example.com", "07222222222", "Addr B")
        service.delete_supplier(first.supplier_id)
        third = service.add_supplier("C", "C", "c@example.com", "07333333333", "Addr C")

        self.assertEqual(second.supplier_id, "S002")
        self.assertEqual(third.supplier_id, "S003")


if __name__ == "__main__":
    unittest.main()
