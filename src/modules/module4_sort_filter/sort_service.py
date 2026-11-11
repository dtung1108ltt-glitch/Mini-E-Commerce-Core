"""
Sort and Filter Service
Coordinates filtering and benchmark execution across all sorting algorithms.
Produces tabular comparisons and timing metrics.
"""
import time
from typing import List, Dict, Any, Optional
from src.core.product import Product
from src.modules.module1_catalog.inventory_service import InventoryService
from src.modules.module4_sort_filter.filters import ProductFilter
from src.modules.module4_sort_filter.basic_sorts import bubble_sort, selection_sort, insertion_sort
from src.modules.module4_sort_filter.advanced_sorts import merge_sort, quick_sort


class SortFilterService:
    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    def filter_catalog(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        in_stock_only: bool = False
    ) -> List[Product]:
        raw_items = list(self.inventory_service.catalog.iter_products())
        return ProductFilter.filter_combined(
            raw_items,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            max_rating=max_rating,
            in_stock_only=in_stock_only
        )

    def run_sort_benchmark(self, sample_size: int = 5000, by: str = "price", ascending: bool = True) -> Dict[str, Any]:
        """
        Run all implemented sorting algorithms on the same dataset slice.
        For large sample sizes (e.g. > 10,000), basic O(n²) sorts are evaluated on smaller sub-samples
        or extrapolated to protect responsiveness.
        """
        all_prods = list(self.inventory_service.catalog.iter_products())
        if not all_prods:
            return {"error": "Catalog is empty. Please load dataset first."}

        dataset = all_prods[:sample_size]
        actual_size = len(dataset)
        results: Dict[str, Any] = {
            "sample_size": actual_size,
            "sort_key": by,
            "ascending": ascending,
            "algorithms": {}
        }

        # 1. Advanced: QuickSort
        t0 = time.perf_counter()
        qs_res = quick_sort(dataset, by=by, ascending=ascending)
        qs_time = time.perf_counter() - t0
        results["algorithms"]["QuickSort (O(n log n))"] = {
            "time_sec": round(qs_time, 5),
            "time_ms": round(qs_time * 1000, 2),
            "complexity": "O(n log n)",
            "verified_sorted": self._is_sorted(qs_res, by, ascending)
        }

        # 2. Advanced: MergeSort
        t0 = time.perf_counter()
        ms_res = merge_sort(dataset, by=by, ascending=ascending)
        ms_time = time.perf_counter() - t0
        results["algorithms"]["MergeSort (O(n log n))"] = {
            "time_sec": round(ms_time, 5),
            "time_ms": round(ms_time * 1000, 2),
            "complexity": "O(n log n)",
            "verified_sorted": self._is_sorted(ms_res, by, ascending)
        }

        # 3. Builtin Python TimSort (baseline)
        t0 = time.perf_counter()
        key_fn = lambda p: getattr(p, by)
        ts_res = sorted(dataset, key=key_fn, reverse=not ascending)
        ts_time = time.perf_counter() - t0
        results["algorithms"]["Python TimSort (C-Level)"] = {
            "time_sec": round(ts_time, 5),
            "time_ms": round(ts_time * 1000, 2),
            "complexity": "O(n log n)",
            "verified_sorted": self._is_sorted(ts_res, by, ascending)
        }

        # 4. Basic sorts: run up to 5,000 items directly
        basic_limit = min(actual_size, 3000)
        sub_dataset = dataset[:basic_limit]

        # Insertion Sort
        t0 = time.perf_counter()
        is_res = insertion_sort(sub_dataset, by=by, ascending=ascending)
        is_time = time.perf_counter() - t0
        results["algorithms"][f"Insertion Sort (N={basic_limit})"] = {
            "time_sec": round(is_time, 5),
            "time_ms": round(is_time * 1000, 2),
            "complexity": "O(n²)",
            "extrapolated_at_100k_sec": round(is_time * ((100000 / basic_limit) ** 2), 1),
            "verified_sorted": self._is_sorted(is_res, by, ascending)
        }

        # Selection Sort
        t0 = time.perf_counter()
        ss_res = selection_sort(sub_dataset, by=by, ascending=ascending)
        ss_time = time.perf_counter() - t0
        results["algorithms"][f"Selection Sort (N={basic_limit})"] = {
            "time_sec": round(ss_time, 5),
            "time_ms": round(ss_time * 1000, 2),
            "complexity": "O(n²)",
            "extrapolated_at_100k_sec": round(ss_time * ((100000 / basic_limit) ** 2), 1),
            "verified_sorted": self._is_sorted(ss_res, by, ascending)
        }

        # Bubble Sort (smaller sample for responsiveness)
        bubble_limit = min(actual_size, 1500)
        bubble_sub = dataset[:bubble_limit]
        t0 = time.perf_counter()
        bs_res = bubble_sort(bubble_sub, by=by, ascending=ascending)
        bs_time = time.perf_counter() - t0
        results["algorithms"][f"Bubble Sort (N={bubble_limit})"] = {
            "time_sec": round(bs_time, 5),
            "time_ms": round(bs_time * 1000, 2),
            "complexity": "O(n²)",
            "extrapolated_at_100k_sec": round(bs_time * ((100000 / bubble_limit) ** 2), 1),
            "verified_sorted": self._is_sorted(bs_res, by, ascending)
        }

        return results

    def _is_sorted(self, arr: List[Product], by: str, ascending: bool) -> bool:
        if len(arr) <= 1:
            return True
        key_fn = lambda p: getattr(p, by)
        for i in range(len(arr) - 1):
            v1 = key_fn(arr[i])
            v2 = key_fn(arr[i + 1])
            if ascending and v1 > v2:
                return False
            if not ascending and v1 < v2:
                return False
        return True
