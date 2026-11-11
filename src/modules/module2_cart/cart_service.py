"""
Cart and Flash Sale Order Processing Service
Coordinates Cart operations with LIFO Undo (Stack) and Flash Sale Checkout (Queue FIFO).
"""
import time
from typing import Dict, Any, List, Optional
from src.core.product import Product
from src.modules.module2_cart.stack import LinkedStack
from src.modules.module2_cart.queue import LinkedQueue
from src.modules.module1_catalog.inventory_service import InventoryService


class CartItem:
    __slots__ = ('product', 'quantity')

    def __init__(self, product: Product, quantity: int = 1):
        self.product = product
        self.quantity = quantity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product": self.product.to_dict(),
            "quantity": self.quantity,
            "subtotal": self.product.price * self.quantity
        }


class CartService:
    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service
        self.cart_items: Dict[int, CartItem] = {}  # product_id -> CartItem
        self.undo_stack = LinkedStack()            # Stores removed/modified actions (LIFO)
        self.checkout_queue = LinkedQueue()        # Incoming orders awaiting processing (FIFO)
        self.processing_logs: List[Dict[str, Any]] = []

    def add_to_cart(self, product_id: int, quantity: int = 1) -> bool:
        """Add a product from the inventory into the shopping cart."""
        product = self.inventory_service.get_product_by_id(product_id)
        if product is None or product.stock <= 0:
            return False

        if product_id in self.cart_items:
            new_qty = self.cart_items[product_id].quantity + quantity
            if new_qty > product.stock:
                return False
            self.cart_items[product_id].quantity = new_qty
        else:
            if quantity > product.stock:
                return False
            self.cart_items[product_id] = CartItem(product, quantity)
        return True

    def remove_from_cart(self, product_id: int) -> Optional[CartItem]:
        """Remove a product from cart and record on Undo Stack (LIFO)."""
        if product_id not in self.cart_items:
            return None
        item = self.cart_items.pop(product_id)
        # Push to undo stack
        self.undo_stack.push({
            "action": "remove",
            "product": item.product,
            "quantity": item.quantity,
            "timestamp": time.time()
        })
        return item

    def undo_remove(self) -> Optional[Dict[str, Any]]:
        """Pop the most recent removal from the Undo Stack and restore the item."""
        if self.undo_stack.is_empty():
            return None
        last_action = self.undo_stack.pop()
        if last_action and last_action.get("action") == "remove":
            prod = last_action["product"]
            qty = last_action["quantity"]
            if prod.id in self.cart_items:
                self.cart_items[prod.id].quantity += qty
            else:
                self.cart_items[prod.id] = CartItem(prod, qty)
            return {
                "restored_product_id": prod.id,
                "restored_name": prod.name,
                "quantity": qty
            }
        return None

    def get_cart_summary(self) -> Dict[str, Any]:
        items_list = [item.to_dict() for item in self.cart_items.values()]
        total_amount = sum(item["subtotal"] for item in items_list)
        total_items = sum(item["quantity"] for item in items_list)
        return {
            "items": items_list,
            "total_items": total_items,
            "total_amount": total_amount,
            "undo_stack_size": len(self.undo_stack)
        }

    # ================= Flash Sale & Checkout Queue (FIFO) =================

    def submit_order(self, customer_name: str, items: Optional[List[Dict[str, Any]]] = None) -> str:
        """Enqueue an order into the Flash Sale checkout queue (FIFO)."""
        order_items = []
        if items:
            for it in items:
                prod = self.inventory_service.get_product_by_id(it["product_id"])
                if prod:
                    order_items.append({"product": prod, "quantity": it.get("quantity", 1)})
        else:
            # Use current cart contents
            for item in self.cart_items.values():
                order_items.append({"product": item.product, "quantity": item.quantity})
            # Clear active cart upon checkout submission
            self.cart_items.clear()
            self.undo_stack.clear()

        order_id = f"ORD-{int(time.time()*1000) % 1000000:06d}-{len(self.checkout_queue)+1:03d}"
        order_payload = {
            "order_id": order_id,
            "customer_name": customer_name,
            "items": order_items,
            "timestamp": time.time(),
            "status": "QUEUED"
        }
        self.checkout_queue.enqueue(order_payload)
        return order_id

    def process_next_order(self) -> Optional[Dict[str, Any]]:
        """Process one order at the front of the FIFO queue."""
        order = self.checkout_queue.dequeue()
        if not order:
            return None

        order_id = order["order_id"]
        success = True
        reason = ""
        total_charged = 0.0

        # Validate stock for all items in order
        for item in order["items"]:
            prod: Product = item["product"]
            req_qty: int = item["quantity"]
            if prod.stock < req_qty:
                success = False
                reason = f"Out of stock for [{prod.id}] {prod.name} (Requested {req_qty}, available {prod.stock})"
                break

        if success:
            # Decrement stock
            for item in order["items"]:
                prod: Product = item["product"]
                req_qty: int = item["quantity"]
                prod.stock -= req_qty
                total_charged += prod.price * req_qty
            order["status"] = "SUCCESS"
            log_entry = {
                "order_id": order_id,
                "customer": order["customer_name"],
                "status": "SUCCESS",
                "amount": total_charged,
                "items_count": len(order["items"]),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "detail": "Flash sale purchase confirmed. Stock decremented."
            }
        else:
            order["status"] = "REJECTED"
            log_entry = {
                "order_id": order_id,
                "customer": order["customer_name"],
                "status": "REJECTED",
                "amount": 0.0,
                "items_count": len(order["items"]),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "detail": reason
            }

        self.processing_logs.append(log_entry)
        return log_entry

    def process_all_orders(self) -> List[Dict[str, Any]]:
        """Process all queued flash sale orders until the queue is empty."""
        processed = []
        while not self.checkout_queue.is_empty():
            log = self.process_next_order()
            if log:
                processed.append(log)
        return processed

    def get_queue_status(self) -> Dict[str, Any]:
        return {
            "queued_orders_count": len(self.checkout_queue),
            "queued_orders": [
                {
                    "order_id": o["order_id"],
                    "customer": o["customer_name"],
                    "items_count": len(o["items"]),
                    "queued_at": time.strftime("%H:%M:%S", time.localtime(o["timestamp"]))
                }
                for o in self.checkout_queue.to_list()
            ],
            "recent_logs": self.processing_logs[-20:]
        }
