"""
Tests for Module 2: Cart & Order Processing (Stack Undo + Queue Flash Sale)
"""
import pytest
from src.core.product import Product
from src.modules.module1_catalog.inventory_service import InventoryService
from src.modules.module2_cart.stack import LinkedStack
from src.modules.module2_cart.queue import LinkedQueue
from src.modules.module2_cart.cart_service import CartService


def test_linked_stack_lifo():
    stack = LinkedStack()
    assert stack.is_empty()
    assert len(stack) == 0

    stack.push(10)
    stack.push(20)
    stack.push(30)
    assert len(stack) == 3
    assert stack.peek() == 30

    assert stack.pop() == 30
    assert stack.pop() == 20
    assert stack.pop() == 10
    assert stack.pop() is None
    assert stack.is_empty()


def test_linked_queue_fifo():
    queue = LinkedQueue()
    assert queue.is_empty()
    assert len(queue) == 0

    queue.enqueue("order_1")
    queue.enqueue("order_2")
    queue.enqueue("order_3")
    assert len(queue) == 3
    assert queue.peek() == "order_1"

    assert queue.dequeue() == "order_1"
    assert queue.dequeue() == "order_2"
    assert queue.dequeue() == "order_3"
    assert queue.dequeue() is None
    assert queue.is_empty()


def test_cart_service_undo_and_flash_sale():
    inv = InventoryService()
    p1 = Product(1, "Laptop Pro", 20000000, 3, 4.9)
    p2 = Product(2, "Mouse Wireless", 500000, 10, 4.5)
    inv.add_product(p1)
    inv.add_product(p2)

    cart_svc = CartService(inv)

    # 1. Add to cart
    assert cart_svc.add_to_cart(1, 2) is True
    assert cart_svc.add_to_cart(2, 1) is True
    summary = cart_svc.get_cart_summary()
    assert summary["total_items"] == 3

    # 2. Remove from cart (LIFO pushed to stack)
    removed = cart_svc.remove_from_cart(1)
    assert removed is not None
    assert removed.product.id == 1
    assert cart_svc.get_cart_summary()["total_items"] == 1
    assert len(cart_svc.undo_stack) == 1

    # 3. Undo remove
    restored = cart_svc.undo_remove()
    assert restored is not None
    assert restored["restored_product_id"] == 1
    assert cart_svc.get_cart_summary()["total_items"] == 3

    # 4. Flash sale checkout queue
    order_id = cart_svc.submit_order("Tran Van B")
    assert order_id.startswith("ORD-")
    assert len(cart_svc.checkout_queue) == 1
    assert len(cart_svc.cart_items) == 0  # Cart cleared

    # 5. Process flash sale order (success case)
    log = cart_svc.process_next_order()
    assert log["status"] == "SUCCESS"
    assert p1.stock == 1  # 3 - 2 = 1 left
    assert p2.stock == 9  # 10 - 1 = 9 left

    # 6. Out of stock case
    cart_svc.submit_order("Customer C", items=[{"product_id": 1, "quantity": 5}])
    log_fail = cart_svc.process_next_order()
    assert log_fail["status"] == "REJECTED"
    assert "Out of stock" in log_fail["detail"]
