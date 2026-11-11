"""
Tree Index Service
Maintains BST and AVL indexes for high-speed O(log n) product retrieval by ID.
Provides comparative metrics (tree height, node count, lookup speeds).
"""
import time
from typing import Optional, Dict, Any, List
from src.core.product import Product
from src.modules.module3_tree.bst import BinarySearchTree
from src.modules.module3_tree.avl import AVLTree
from src.modules.module1_catalog.inventory_service import InventoryService


class TreeIndexService:
    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service
        self.bst = BinarySearchTree()
        self.avl = AVLTree()

    def build_indexes(self, max_items: Optional[int] = None) -> Dict[str, Any]:
        """Build both BST and AVL indexes from the current inventory catalog."""
        self.bst.clear()
        self.avl.clear()

        # Build BST
        t0 = time.perf_counter()
        count = 0
        for prod in self.inventory_service.catalog.iter_products():
            self.bst.insert(prod)
            count += 1
            if max_items and count >= max_items:
                break
        bst_time = time.perf_counter() - t0

        # Build AVL
        t0 = time.perf_counter()
        count = 0
        for prod in self.inventory_service.catalog.iter_products():
            self.avl.insert(prod)
            count += 1
            if max_items and count >= max_items:
                break
        avl_time = time.perf_counter() - t0

        return {
            "indexed_count": count,
            "bst": {
                "build_time_sec": round(bst_time, 4),
                "height": self.bst.height(),
                "node_count": len(self.bst)
            },
            "avl": {
                "build_time_sec": round(avl_time, 4),
                "height": self.avl.height(),
                "rotations": self.avl.rotations_count,
                "node_count": len(self.avl)
            }
        }

    def search_by_id(self, product_id: int) -> Dict[str, Any]:
        """Lookup by ID across both BST and AVL, measuring latency."""
        t0 = time.perf_counter_ns()
        bst_res = self.bst.search(product_id)
        bst_ns = time.perf_counter_ns() - t0

        t0 = time.perf_counter_ns()
        avl_res = self.avl.search(product_id)
        avl_ns = time.perf_counter_ns() - t0

        found = avl_res or bst_res
        return {
            "product_id": product_id,
            "found": found is not None,
            "product": found.to_dict() if found else None,
            "bst_latency_ns": bst_ns,
            "avl_latency_ns": avl_ns
        }

    def get_traversals(self, tree_type: str = "bst", traversal: str = "in_order", limit: int = 15) -> List[Dict[str, Any]]:
        tree = self.bst if tree_type.lower() == "bst" else self.avl
        if traversal == "pre_order" and hasattr(tree, "pre_order"):
            items = tree.pre_order(limit)
        elif traversal == "post_order" and hasattr(tree, "post_order"):
            items = tree.post_order(limit)
        else:
            items = tree.in_order(limit)
        return [p.to_dict() for p in items]
