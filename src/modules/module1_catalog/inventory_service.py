"""
Inventory Service
Coordinates catalog loading from CSV, pagination, product additions and deletions, and memory release.
"""
import csv
import time
from typing import Optional, List, Dict, Any, Tuple
from src.core.product import Product
from src.core.memory_manager import MemoryProfiler
from src.modules.module1_catalog.doubly_linked_list import DoublyLinkedList


class InventoryService:
    def __init__(self):
        self.catalog = DoublyLinkedList()
        self.profiler = MemoryProfiler.get_instance()
        self.loaded_filepath: Optional[str] = None

    def load_from_csv(self, filepath: str, limit: Optional[int] = None) -> Tuple[int, float]:
        """
        Load products from a CSV file into the Doubly Linked List.
        Returns: (number_of_products_loaded, elapsed_seconds)
        """
        self.profiler.take_snapshot("before_catalog_load")
        start_time = time.perf_counter()

        # Clear existing catalog if any
        if not self.catalog.is_empty():
            self.catalog.clear()

        loaded_count = 0
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prod = Product(
                    product_id=int(row["id"]),
                    name=row["name"],
                    price=float(row["price"]),
                    stock=int(row["stock"]),
                    rating=float(row["rating"])
                )
                self.catalog.add_tail(prod)
                loaded_count += 1
                if limit and loaded_count >= limit:
                    break

        elapsed = time.perf_counter() - start_time
        self.loaded_filepath = filepath
        self.profiler.take_snapshot(f"after_catalog_load_{loaded_count}_items")
        return loaded_count, elapsed

    def add_product(self, product: Product, position: str = "tail") -> None:
        if position.lower() == "head":
            self.catalog.add_head(product)
        else:
            self.catalog.add_tail(product)

    def delete_product(self, product_id: int) -> Optional[Product]:
        return self.catalog.delete_by_id(product_id)

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        node = self.catalog.find_node_by_id(product_id)
        return node.data if node else None

    def get_page(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        total_items = len(self.catalog)
        total_pages = max(1, (total_items + page_size - 1) // page_size)
        items = self.catalog.paginate(page, page_size)
        return {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "items": [item.to_dict() for item in items]
        }

    def cleanup_inventory(self) -> Dict[str, Any]:
        """Explicitly clear linked list and release memory via garbage collector."""
        count = self.catalog.clear()
        gc_stats = self.profiler.force_cleanup()
        return {
            "nodes_released": count,
            "gc_stats": gc_stats
        }

    def count(self) -> int:
        return len(self.catalog)
