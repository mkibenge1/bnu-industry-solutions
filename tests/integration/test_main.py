import unittest
from unittest.mock import MagicMock, patch

import main


class TestMain(unittest.TestCase):
# test for main initializes services and starts menu
    @patch("main.Menu")
    @patch("main.OrderService")
    @patch("main.FinanceService")
    @patch("main.InventoryService")
    @patch("main.SupplierService")
    # test for main initializes services and starts menu
    def test_main_initializes_services_and_starts_menu(
        self,
        mock_supplier_service,
        mock_inventory_service,
        mock_finance_service,
        mock_order_service,
        mock_menu,
    ):
        menu_instance = mock_menu.return_value
        menu_instance.run = MagicMock()

        main.main()

        mock_supplier_service.assert_called_once()
        mock_inventory_service.assert_called_once()
        mock_finance_service.assert_called_once()
        mock_order_service.assert_called_once_with(
            mock_inventory_service.return_value,
            mock_supplier_service.return_value,
            mock_finance_service.return_value,
        )
        mock_menu.assert_called_once_with(
            mock_supplier_service.return_value,
            mock_inventory_service.return_value,
            mock_order_service.return_value,
            mock_finance_service.return_value,
        )
        menu_instance.run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
