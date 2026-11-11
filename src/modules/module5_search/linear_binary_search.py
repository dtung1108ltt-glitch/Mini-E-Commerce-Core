"""
Linear Search and Binary Search Implementations
For comparative benchmarking against BST search and Hash Table search.
"""
from typing import List, Optional, Tuple
from src.core.product import Product


def linear_search_by_id(products: List[Product], target_id: int) -> Tuple[Optional[Product], int]:
    """
    Linear Search: Sequentially scans the list.
    Time Complexity: O(n), Space Complexity: O(1).
    Returns (Product, comparisons_count).
    """
    comparisons = 0
    for p in products:
        comparisons += 1
        if p.id == target_id:
            return p, comparisons
    return None, comparisons


def linear_search_by_name(products: List[Product], target_name: str) -> Tuple[Optional[Product], int]:
    """
    Linear Search by Product Name.
    Time Complexity: O(n), comparisons returned.
    """
    comparisons = 0
    target_lower = target_name.lower().strip()
    for p in products:
        comparisons += 1
        if p.name.lower() == target_lower:
            return p, comparisons
    return None, comparisons


def binary_search_by_id(sorted_products: List[Product], target_id: int) -> Tuple[Optional[Product], int]:
    """
    Binary Search: Divide-and-conquer on an ID-sorted array.
    Time Complexity: O(log n), Space Complexity: O(1).
    Returns (Product, comparisons_count).
    """
    low = 0
    high = len(sorted_products) - 1
    comparisons = 0

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_val = sorted_products[mid].id

        if mid_val == target_id:
            return sorted_products[mid], comparisons
        elif mid_val < target_id:
            low = mid + 1
        else:
            high = mid - 1

    return None, comparisons
