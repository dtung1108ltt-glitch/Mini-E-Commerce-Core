"""
Doubly Linked List Implementation for Catalog & Inventory Management
Stores products dynamically without static arrays.
Supports O(1) head/tail insertions, O(n) search by ID, O(1) node unlinking, and explicit memory teardown.
"""
from typing import Optional, Generator, List
from src.core.product import Product


class Node:
    __slots__ = ('data', 'prev', 'next')

    def __init__(self, data: Product):
        self.data: Product = data
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None


class DoublyLinkedList:
    __slots__ = ('head', 'tail', '_size')

    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def add_head(self, product: Product) -> None:
        """Insert product at the beginning of the list - O(1)"""
        new_node = Node(product)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1

    def add_tail(self, product: Product) -> None:
        """Insert product at the end of the list - O(1)"""
        new_node = Node(product)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def find_node_by_id(self, product_id: int) -> Optional[Node]:
        """Search for a node by product ID - O(n)"""
        current = self.head
        while current is not None:
            if current.data.id == product_id:
                return current
            current = current.next
        return None

    def delete_by_id(self, product_id: int) -> Optional[Product]:
        """Delete product by ID and return deleted product - O(n) search + O(1) unlink"""
        node_to_delete = self.find_node_by_id(product_id)
        if node_to_delete is None:
            return None

        # Re-link pointers
        if node_to_delete.prev:
            node_to_delete.prev.next = node_to_delete.next
        else:
            self.head = node_to_delete.next

        if node_to_delete.next:
            node_to_delete.next.prev = node_to_delete.prev
        else:
            self.tail = node_to_delete.prev

        self._size -= 1
        deleted_product = node_to_delete.data

        # Explicitly break internal references to aid garbage collection
        node_to_delete.prev = None
        node_to_delete.next = None
        return deleted_product

    def paginate(self, page: int = 1, page_size: int = 20) -> List[Product]:
        """Retrieve a specific page of products (1-indexed)"""
        if page < 1 or page_size < 1:
            return []
        
        start_idx = (page - 1) * page_size
        if start_idx >= self._size:
            return []

        results: List[Product] = []
        current = self.head
        idx = 0

        # Traverse to start index
        while current is not None and idx < start_idx:
            current = current.next
            idx += 1

        # Collect page items
        while current is not None and len(results) < page_size:
            results.append(current.data)
            current = current.next

        return results

    def iter_products(self) -> Generator[Product, None, None]:
        """Yield products one by one without creating giant array in memory"""
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def clear(self) -> int:
        """
        Explicit memory cleanup routine.
        Traverses and severs all bi-directional references to avoid cyclical retain cycles.
        Returns the number of nodes cleared.
        """
        cleared_count = 0
        current = self.head
        while current is not None:
            next_node = current.next
            current.prev = None
            current.next = None
            current = next_node
            cleared_count += 1

        self.head = None
        self.tail = None
        self._size = 0
        return cleared_count
