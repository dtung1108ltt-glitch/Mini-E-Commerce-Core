"""
Binary Search Tree (BST) Implementation
Keyed by Product ID.
Implements recursive Insert, Search, Delete, and Pre-order, In-order, Post-order traversals.
Includes height calculation and node counting.
"""
from typing import Optional, List, Callable, Any
from src.core.product import Product


class BSTNode:
    __slots__ = ('key', 'product', 'left', 'right')

    def __init__(self, product: Product):
        self.key: int = product.id
        self.product: Product = product
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class BinarySearchTree:
    __slots__ = ('root', '_size')

    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.root is None

    def insert(self, product: Product) -> None:
        """Insert product by ID with recursion-depth resilience."""
        new_node = BSTNode(product)
        if self.root is None:
            self.root = new_node
            self._size += 1
            return

        curr = self.root
        while True:
            if product.id < curr.key:
                if curr.left is None:
                    curr.left = new_node
                    self._size += 1
                    break
                curr = curr.left
            elif product.id > curr.key:
                if curr.right is None:
                    curr.right = new_node
                    self._size += 1
                    break
                curr = curr.right
            else:
                curr.product = product
                break

    def search(self, product_id: int) -> Optional[Product]:
        """Search product by ID - average O(log n), worst-case O(n) without recursion limits."""
        curr = self.root
        while curr:
            if product_id == curr.key:
                return curr.product
            elif product_id < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def delete(self, product_id: int) -> Optional[Product]:
        """Delete product by ID using recursion. Returns deleted product if found."""
        deleted_prod: List[Optional[Product]] = [None]

        def _min_value_node(node: BSTNode) -> BSTNode:
            current = node
            while current.left is not None:
                current = current.left
            return current

        def _delete(node: Optional[BSTNode], pid: int) -> Optional[BSTNode]:
            if node is None:
                return None

            if pid < node.key:
                node.left = _delete(node.left, pid)
            elif pid > node.key:
                node.right = _delete(node.right, pid)
            else:
                # Node with matching key found
                if deleted_prod[0] is None:
                    deleted_prod[0] = node.product
                self._size -= 1

                # Case 1: Node with only one child or no child
                if node.left is None:
                    return node.right
                elif node.right is None:
                    return node.left

                # Case 2: Node with two children -> find in-order successor
                temp = _min_value_node(node.right)
                node.key = temp.key
                node.product = temp.product
                # Delete successor
                node.right = _delete(node.right, temp.key)
                self._size += 1  # Offset inner size decrement

            return node

        self.root = _delete(self.root, product_id)
        return deleted_prod[0]

    # Recursive Traversals
    def pre_order(self, limit: Optional[int] = None) -> List[Product]:
        result: List[Product] = []

        def _traverse(node: Optional[BSTNode]):
            if node is None or (limit is not None and len(result) >= limit):
                return
            result.append(node.product)
            _traverse(node.left)
            _traverse(node.right)

        _traverse(self.root)
        return result

    def in_order(self, limit: Optional[int] = None) -> List[Product]:
        result: List[Product] = []

        def _traverse(node: Optional[BSTNode]):
            if node is None or (limit is not None and len(result) >= limit):
                return
            _traverse(node.left)
            if limit is None or len(result) < limit:
                result.append(node.product)
            _traverse(node.right)

        _traverse(self.root)
        return result

    def post_order(self, limit: Optional[int] = None) -> List[Product]:
        result: List[Product] = []

        def _traverse(node: Optional[BSTNode]):
            if node is None or (limit is not None and len(result) >= limit):
                return
            _traverse(node.left)
            _traverse(node.right)
            if limit is None or len(result) < limit:
                result.append(node.product)

        _traverse(self.root)
        return result

    def height(self) -> int:
        """Calculate max depth/height iteratively using BFS (queue) to avoid recursion overflow."""
        if self.root is None:
            return 0
        from collections import deque
        queue = deque([self.root])
        h = 0
        while queue:
            h += 1
            for _ in range(len(queue)):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
        return h

    def clear(self) -> None:
        """Clear the tree iteratively and break node references."""
        if not self.root:
            return
        from collections import deque
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
            node.left = None
            node.right = None
        self.root = None
        self._size = 0
