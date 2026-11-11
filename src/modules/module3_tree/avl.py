"""
AVL Tree (Adelson-Velsky and Landis) Implementation
Self-balancing binary search tree maintaining height balance |h_L - h_R| <= 1.
Implements Right Rotation, Left Rotation, Left-Right, and Right-Left rotations.
Guarantees O(log n) worst-case time for Insert, Search, and Delete.
"""
from typing import Optional, List
from src.core.product import Product


class AVLNode:
    __slots__ = ('key', 'product', 'left', 'right', 'height')

    def __init__(self, product: Product):
        self.key: int = product.id
        self.product: Product = product
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height: int = 1


class AVLTree:
    __slots__ = ('root', '_size', 'rotations_count')

    def __init__(self):
        self.root: Optional[AVLNode] = None
        self._size: int = 0
        self.rotations_count: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.root is None

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

    def _right_rotate(self, y: AVLNode) -> AVLNode:
        r"""
            y                              x
           / \                           /   \
          x   T3   -- Right Rotate ->   T1    y
         / \                                 / \
        T1  T2                              T2  T3
        """
        self.rotations_count += 1
        x = y.left
        assert x is not None
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        self._update_height(y)
        self._update_height(x)
        return x

    def _left_rotate(self, x: AVLNode) -> AVLNode:
        r"""
          x                                y
         / \                             /   \
        T1  y      -- Left Rotate ->    x     T3
           / \                         / \
          T2  T3                      T1  T2
        """
        self.rotations_count += 1
        y = x.right
        assert y is not None
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        self._update_height(x)
        self._update_height(y)
        return y

    def insert(self, product: Product) -> None:
        """Insert product into AVL tree with rebalancing - O(log n)"""
        def _insert(node: Optional[AVLNode], prod: Product) -> AVLNode:
            if not node:
                self._size += 1
                return AVLNode(prod)

            if prod.id < node.key:
                node.left = _insert(node.left, prod)
            elif prod.id > node.key:
                node.right = _insert(node.right, prod)
            else:
                node.product = prod
                return node

            # Update height of this ancestor node
            self._update_height(node)

            # Check balance factor
            balance = self._get_balance(node)

            # Case 1: Left Left (LL)
            if balance > 1 and node.left and prod.id < node.left.key:
                return self._right_rotate(node)

            # Case 2: Right Right (RR)
            if balance < -1 and node.right and prod.id > node.right.key:
                return self._left_rotate(node)

            # Case 3: Left Right (LR)
            if balance > 1 and node.left and prod.id > node.left.key:
                node.left = self._left_rotate(node.left)
                return self._right_rotate(node)

            # Case 4: Right Left (RL)
            if balance < -1 and node.right and prod.id < node.right.key:
                node.right = self._right_rotate(node.right)
                return self._left_rotate(node)

            return node

        self.root = _insert(self.root, product)

    def search(self, product_id: int) -> Optional[Product]:
        """Search product by ID - guaranteed O(log n)"""
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
        """Delete product by ID with rebalancing - O(log n)"""
        deleted_prod: List[Optional[Product]] = [None]

        def _min_node(node: AVLNode) -> AVLNode:
            curr = node
            while curr.left:
                curr = curr.left
            return curr

        def _delete(node: Optional[AVLNode], pid: int) -> Optional[AVLNode]:
            if not node:
                return None

            if pid < node.key:
                node.left = _delete(node.left, pid)
            elif pid > node.key:
                node.right = _delete(node.right, pid)
            else:
                if deleted_prod[0] is None:
                    deleted_prod[0] = node.product
                self._size -= 1

                # One or zero child
                if not node.left:
                    return node.right
                elif not node.right:
                    return node.left

                # Two children
                temp = _min_node(node.right)
                node.key = temp.key
                node.product = temp.product
                node.right = _delete(node.right, temp.key)
                self._size += 1

            if not node:
                return None

            self._update_height(node)
            balance = self._get_balance(node)

            # Rebalance
            if balance > 1 and self._get_balance(node.left) >= 0:
                return self._right_rotate(node)
            if balance > 1 and self._get_balance(node.left) < 0:
                assert node.left is not None
                node.left = self._left_rotate(node.left)
                return self._right_rotate(node)
            if balance < -1 and self._get_balance(node.right) <= 0:
                return self._left_rotate(node)
            if balance < -1 and self._get_balance(node.right) > 0:
                assert node.right is not None
                node.right = self._right_rotate(node.right)
                return self._left_rotate(node)

            return node

        self.root = _delete(self.root, product_id)
        return deleted_prod[0]

    def in_order(self, limit: Optional[int] = None) -> List[Product]:
        res: List[Product] = []

        def _in_order(node: Optional[AVLNode]):
            if not node or (limit and len(res) >= limit):
                return
            _in_order(node.left)
            if not limit or len(res) < limit:
                res.append(node.product)
            _in_order(node.right)

        _in_order(self.root)
        return res

    def height(self) -> int:
        return self._get_height(self.root)

    def clear(self) -> None:
        def _clear(node: Optional[AVLNode]):
            if node:
                _clear(node.left)
                _clear(node.right)
                node.left = None
                node.right = None
        _clear(self.root)
        self.root = None
        self._size = 0
