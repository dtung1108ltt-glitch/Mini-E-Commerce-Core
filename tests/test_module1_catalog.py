"""
Tests for Module 1: Catalog & Inventory Management (Doubly Linked List)
"""
import pytest
from src.core.product import Product
from src.modules.module1_catalog.doubly_linked_list import DoublyLinkedList
from src.modules.module1_catalog.inventory_service import InventoryService


def test_doubly_linked_list_basic_operations():
    dll = DoublyLinkedList()
    assert dll.is_empty()
    assert len(dll) == 0

    p1 = Product(1, "Product 1", 10000, 10, 4.5)
    p2 = Product(2, "Product 2", 20000, 5, 4.0)
    p3 = Product(3, "Product 3", 30000, 15, 5.0)

    # Test add head and tail
    dll.add_head(p2)  # [p2]
    dll.add_head(p1)  # [p1, p2]
    dll.add_tail(p3)  # [p1, p2, p3]

    assert len(dll) == 3
    assert dll.head.data.id == 1
    assert dll.tail.data.id == 3

    # Test find
    node = dll.find_node_by_id(2)
    assert node is not None
    assert node.data.name == "Product 2"

    # Test pagination
    page1 = dll.paginate(page=1, page_size=2)
    assert len(page1) == 2
    assert page1[0].id == 1
    assert page1[1].id == 2

    page2 = dll.paginate(page=2, page_size=2)
    assert len(page2) == 1
    assert page2[0].id == 3

    # Test deletion
    deleted = dll.delete_by_id(2)
    assert deleted is not None
    assert deleted.id == 2
    assert len(dll) == 2

    # Verify links
    assert dll.head.next.data.id == 3
    assert dll.tail.prev.data.id == 1

    # Test clear (explicit memory cleanup)
    cleared = dll.clear()
    assert cleared == 2
    assert dll.is_empty()
    assert dll.head is None
    assert dll.tail is None


def test_inventory_service_operations(tmp_path):
    # Create temporary CSV
    csv_file = tmp_path / "test_products.csv"
    csv_file.write_text("id,name,price,stock,rating\n1,Alpha,15000,10,4.2\n2,Beta,25000,20,4.8\n")

    service = InventoryService()
    count, sec = service.load_from_csv(str(csv_file))
    assert count == 2
    assert service.count() == 2

    # Add head
    service.add_product(Product(0, "Zero", 5000, 5, 3.5), position="head")
    assert service.count() == 3
    assert service.catalog.head.data.id == 0

    # Delete
    del_prod = service.delete_product(1)
    assert del_prod.name == "Alpha"
    assert service.count() == 2

    # Cleanup
    clean_res = service.cleanup_inventory()
    assert clean_res["nodes_released"] == 2
    assert service.count() == 0
