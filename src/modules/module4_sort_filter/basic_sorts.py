"""
Basic O(n²) Sorting Algorithms
Implements Bubble Sort, Selection Sort, and Insertion Sort.
Each function operates on a shallow copy of the list and supports sorting by 'price', 'rating', or 'id'.
"""
from typing import List, Callable, Any
from src.core.product import Product


def _get_key_fn(by: str) -> Callable[[Product], Any]:
    if by == "price":
        return lambda p: p.price
    elif by == "rating":
        return lambda p: p.rating
    elif by == "stock":
        return lambda p: p.stock
    return lambda p: p.id


def bubble_sort(arr: List[Product], by: str = "price", ascending: bool = True) -> List[Product]:
    """Bubble Sort: Repeatedly steps through the list, compares adjacent pairs and swaps."""
    n = len(arr)
    result = list(arr)
    key_fn = _get_key_fn(by)

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            val1 = key_fn(result[j])
            val2 = key_fn(result[j + 1])
            condition = (val1 > val2) if ascending else (val1 < val2)
            if condition:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break
    return result


def selection_sort(arr: List[Product], by: str = "price", ascending: bool = True) -> List[Product]:
    """Selection Sort: Finds the minimum/maximum element and places it at the sorted boundary."""
    n = len(arr)
    result = list(arr)
    key_fn = _get_key_fn(by)

    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            val_j = key_fn(result[j])
            val_target = key_fn(result[target_idx])
            condition = (val_j < val_target) if ascending else (val_j > val_target)
            if condition:
                target_idx = j
        if target_idx != i:
            result[i], result[target_idx] = result[target_idx], result[i]
    return result


def insertion_sort(arr: List[Product], by: str = "price", ascending: bool = True) -> List[Product]:
    """Insertion Sort: Builds the sorted array in-place one element at a time."""
    n = len(arr)
    result = list(arr)
    key_fn = _get_key_fn(by)

    for i in range(1, n):
        key_item = result[i]
        key_val = key_fn(key_item)
        j = i - 1

        while j >= 0:
            val_j = key_fn(result[j])
            condition = (val_j > key_val) if ascending else (val_j < key_val)
            if condition:
                result[j + 1] = result[j]
                j -= 1
            else:
                break
        result[j + 1] = key_item

    return result
