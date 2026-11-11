"""
Search Service
Coordinates Hash Table instant indexing, Self-Organizing keyword history,
and head-to-head performance comparisons (Linear vs Binary vs BST vs Hash Table).
"""
import time
from typing import Dict, Any, List, Optional
from src.core.product import Product
from src.modules.module1_catalog.inventory_service import InventoryService
from src.modules.module3_tree.tree_index_service import TreeIndexService
from src.modules.module5_search.hash_table import HashTable
from src.modules.module5_search.self_organizing_list import SelfOrganizingList
from src.modules.module5_search.linear_binary_search import (
    linear_search_by_id,
    linear_search_by_name,
    binary_search_by_id
)


class SearchService:
    def __init__(self, inventory_service: InventoryService, tree_service: Optional[TreeIndexService] = None):
        self.inventory_service = inventory_service
        self.tree_service = tree_service
        self.hash_table = HashTable()
        self.history_mtf = SelfOrganizingList(strategy="MTF")
        self.history_transpose = SelfOrganizingList(strategy="Transpose")
        self.active_history_strategy = "MTF"
        self._sorted_array_cache: Optional[List[Product]] = None

    def build_hash_index(self, max_items: Optional[int] = None) -> Dict[str, Any]:
        """Index all products into the Hash Table keyed by exact Name."""
        self.hash_table.clear()
        t0 = time.perf_counter()
        count = 0
        for p in self.inventory_service.catalog.iter_products():
            self.hash_table.insert(p.name, p)
            count += 1
            if max_items and count >= max_items:
                break
        elapsed = time.perf_counter() - t0
        stats = self.hash_table.get_statistics()
        stats["build_time_sec"] = round(elapsed, 4)
        return stats

    def search_by_name_hash(self, name: str) -> Dict[str, Any]:
        """Instant lookup via Hash Table - average O(1)."""
        clean_name = name.strip()
        t0 = time.perf_counter_ns()
        product = self.hash_table.search(clean_name)
        elapsed_ns = time.perf_counter_ns() - t0

        # Record in history
        probes_mtf = self.history_mtf.record_search(clean_name)
        probes_trans = self.history_transpose.record_search(clean_name)

        return {
            "query": clean_name,
            "found": product is not None,
            "product": product.to_dict() if product else None,
            "latency_ns": elapsed_ns,
            "latency_ms": round(elapsed_ns / 1_000_000, 4),
            "probes_mtf": probes_mtf,
            "probes_transpose": probes_trans
        }

    def compare_search_methods_by_id(self, target_id: int) -> Dict[str, Any]:
        """
        Compare search algorithms on Product ID:
        1. Linear Search (Unsorted DLL / Array) - O(n)
        2. Binary Search (Sorted Array) - O(log n)
        3. BST Search - average O(log n)
        4. AVL Tree Search - guaranteed O(log n)
        """
        raw_list = list(self.inventory_service.catalog.iter_products())
        n = len(raw_list)
        if n == 0:
            return {"error": "Catalog is empty"}

        # 1. Linear Search
        t0 = time.perf_counter_ns()
        p_lin, lin_comps = linear_search_by_id(raw_list, target_id)
        lin_time_ns = time.perf_counter_ns() - t0

        # 2. Binary Search (prepare sorted array if not cached)
        if self._sorted_array_cache is None or len(self._sorted_array_cache) != n:
            self._sorted_array_cache = sorted(raw_list, key=lambda p: p.id)

        t0 = time.perf_counter_ns()
        p_bin, bin_comps = binary_search_by_id(self._sorted_array_cache, target_id)
        bin_time_ns = time.perf_counter_ns() - t0

        # 3. BST Search
        bst_time_ns = 0
        bst_found = False
        if self.tree_service:
            t0 = time.perf_counter_ns()
            p_bst = self.tree_service.bst.search(target_id)
            bst_time_ns = time.perf_counter_ns() - t0
            bst_found = p_bst is not None

        # 4. AVL Tree Search
        avl_time_ns = 0
        avl_found = False
        if self.tree_service:
            t0 = time.perf_counter_ns()
            p_avl = self.tree_service.avl.search(target_id)
            avl_time_ns = time.perf_counter_ns() - t0
            avl_found = p_avl is not None

        return {
            "target_id": target_id,
            "dataset_size": n,
            "results": {
                "Linear Search (O(n))": {
                    "latency_ns": lin_time_ns,
                    "latency_ms": round(lin_time_ns / 1_000_000, 4),
                    "comparisons": lin_comps,
                    "found": p_lin is not None
                },
                "Binary Search (O(log n))": {
                    "latency_ns": bin_time_ns,
                    "latency_ms": round(bin_time_ns / 1_000_000, 4),
                    "comparisons": bin_comps,
                    "found": p_bin is not None
                },
                "BST Search (O(log n) avg)": {
                    "latency_ns": bst_time_ns,
                    "latency_ms": round(bst_time_ns / 1_000_000, 4),
                    "found": bst_found
                },
                "AVL Tree Search (O(log n) strict)": {
                    "latency_ns": avl_time_ns,
                    "latency_ms": round(avl_time_ns / 1_000_000, 4),
                    "found": avl_found
                }
            }
        }

    def get_search_history(self, strategy: str = "MTF", limit: int = 15) -> Dict[str, Any]:
        active_list = self.history_mtf if strategy.upper() == "MTF" else self.history_transpose
        return {
            "strategy": strategy.upper(),
            "metrics": active_list.get_metrics(),
            "items": active_list.get_history(limit)
        }
