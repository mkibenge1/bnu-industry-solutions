from __future__ import annotations
from datetime import datetime
from models.bnu_models import (
    CustomerOrder,
    OrderLine,
    OrderStatus,
    PurchaseOrder,
)
from repositories.order_repository import OrderRepository
from services.finance_service import FinanceService
from services.inventory_service import InventoryService
from services.supplier_service import SupplierService

class OrderService:
    def __init__(
        self,
        inventory_service: InventoryService,
        supplier_service: SupplierService,
        finance_service: FinanceService,
    ) -> None:
        self._inventory_service = inventory_service
        self._supplier_service = supplier_service
        self._finance_service = finance_service
        self._purchase_repository = OrderRepository("data/purchase_orders.json")
        self._customer_repository = OrderRepository("data/customer_orders.json")
        self._purchase_orders: list[PurchaseOrder] = (
            self._purchase_repository.load_purchase_orders()  # Load purchase orders from JSON
        )
        self._customer_orders: list[CustomerOrder] = (
            self._customer_repository.load_customer_orders()  # Load customer orders from JSON
        )

    # Generates a new unique purchase order ID
    def _generate_purchase_order_id(self) -> str:
        return f"PO{len(self._purchase_orders) + 1:03}"

    # Generates a new unique customer order ID
    def _generate_customer_order_id(self) -> str:
        return f"CO{len(self._customer_orders) + 1:03}"

    # Create a new purchase order from a supplier
    def create_purchase_order(
        self,
        supplier_id: str,
        lines: list[OrderLine],
    ) -> PurchaseOrder:
        supplier = self._supplier_service.get_supplier_by_id(supplier_id)
        if supplier is None or not supplier.is_active:
            raise ValueError("Supplier not found or inactive.")

        if not lines:
            raise ValueError("Purchase order must contain at least one line.")

        order = PurchaseOrder(
            order_id=self._generate_purchase_order_id(),
            created_at=datetime.now(),
            supplier_id=supplier_id,
        )

        for line in lines:
            product = self._inventory_service.get_product_by_id(line.product_id)
            if product is None:
                raise ValueError(f"Product {line.product_id} not found.")
            order.add_line(line)

        self._purchase_orders.append(order)
        self._purchase_repository.save_purchase_orders(self._purchase_orders) # Save purchase orders to JSON
        return order

    # Create a new customer order and update stock
    def create_customer_order(
        self,
        customer_name: str,
        customer_email: str,
        lines: list[OrderLine],
    ) -> CustomerOrder:
        if not lines:
            raise ValueError("Customer order must contain at least one line.")

        for line in lines:
            product = self._inventory_service.get_product_by_id(line.product_id)
            if product is None:
                raise ValueError(f"Product {line.product_id} not found.")
            if product.stock_quantity < line.quantity:
                raise ValueError(f"Insufficient stock for product {product.product_id}.")

        order = CustomerOrder(
            order_id=self._generate_customer_order_id(),
            created_at=datetime.now(),
            customer_name=customer_name,
            customer_email=customer_email,
        )

        for line in lines:
            product = self._inventory_service.get_product_by_id(line.product_id)
            if product is None:
                raise ValueError(f"Product {line.product_id} not found.")
            order.add_line(line)
            product.reduce_stock(line.quantity)

        self._customer_orders.append(order)
        self._customer_repository.save_customer_orders(self._customer_orders) # Save customer orders to JSON
        self._inventory_service.save_products() # Save updated product stock

        self._finance_service.record_sale(
            amount=order.total_amount(),
            description=f"Customer order {order.order_id}",
            related_order_id=order.order_id,
        )

        return order

    # Return all purchase orders in memory
    def list_purchase_orders(self) -> list[PurchaseOrder]:
        return self._purchase_orders.copy()

    # Return all customer orders in memory
    def list_customer_orders(self) -> list[CustomerOrder]:
        return self._customer_orders.copy()

    # Find a purchase order by ID
    def get_purchase_order_by_id(self, order_id: str) -> PurchaseOrder | None:
        for order in self._purchase_orders:
            if order.order_id == order_id:
                return order
        return None

    # Find a customer order by ID
    def get_customer_order_by_id(self, order_id: str) -> CustomerOrder | None:
        for order in self._customer_orders:
            if order.order_id == order_id:
                return order
        return None

    # Mark a purchase order as shipped
    def mark_purchase_order_as_shipped(self, order_id: str) -> None:
        order = self.get_purchase_order_by_id(order_id)
        if order is None:
            raise ValueError("Purchase order not found.")
        if order.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be marked as shipped.")

        order.update_status(OrderStatus.SHIPPED)
        self._purchase_repository.save_purchase_orders(self._purchase_orders) # Save order status change

    # Receive a shipped purchase order and update inventory
    def receive_purchase_order(self, order_id: str) -> None:
        order = self.get_purchase_order_by_id(order_id)
        if order is None:
            raise ValueError("Purchase order not found.")
        if order.status != OrderStatus.SHIPPED:
            raise ValueError("Only shipped orders can be marked as delivered.")

        for line in order.lines:
            product = self._inventory_service.get_product_by_id(line.product_id)
            if product is None:
                raise ValueError(f"Product {line.product_id} not found.")
            product.increase_stock(line.quantity)

        self._inventory_service.save_products() # Save updated stock
        order.update_status(OrderStatus.DELIVERED)
        self._purchase_repository.save_purchase_orders(self._purchase_orders) # Save order status change

        self._finance_service.record_expense(
            amount=order.total_amount(),
            description=f"Purchase order {order.order_id}",
            related_order_id=order.order_id,
        )