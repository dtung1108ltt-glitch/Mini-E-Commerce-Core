"""
Advanced O(n log n) Recursive Sorting Algorithms
Implements MergeSort and QuickSort (with Median-of-Three pivot selection and tail-recursion optimization).
"""
import sys
from typing import List, Callable, Any
from src.core.product import Product
from src.modules.module4_sort_filter.basic_sorts import _get_key_fn


def merge_sort(arr: List[Product], by: str = "price", ascending: bool = True) -> List[Product]:
    """
    MergeSort: Divide and conquer algorithm.
    Guaranteed O(n log n) time complexity, stable sorting.
    """
    if len(arr) <= 1:
        return list(arr)

    key_fn = _get_key_fn(by)

    def _merge(left: List[Product], right: List[Product]) -> List[Product]:
        merged: List[Product] = []
        i = j = 0
        n_l, n_r = len(left), len(right)

        while i < n_l and j < n_r:
            val_l = key_fn(left[i])
            val_r = key_fn(right[j])
            condition = (val_l <= val_r) if ascending else (val_l >= val_r)
            if condition:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

        if i < n_l:
            merged.extend(left[i:])
        if j < n_r:
            merged.extend(right[j:])
        return merged

    mid = len(arr) // 2
    left_sorted = merge_sort(arr[:mid], by=by, ascending=ascending)
    right_sorted = merge_sort(arr[mid:], by=by, ascending=ascending)
    return _merge(left_sorted, right_sorted)


def quick_sort(arr: List[Product], by: str = "price", ascending: bool = True) -> List[Product]:
    """
    QuickSort: Divide and conquer with Median-of-Three pivot selection.
    Average O(n log n) time complexity. Median-of-three prevents O(n²) degeneration on sorted data.
    """
    result = list(arr)
    n = len(result)
    if n <= 1:
        return result

    key_fn = _get_key_fn(by)

    def _median_of_three(a: int, b: int, c: int) -> int:
        val_a = key_fn(result[a])
        val_b = key_fn(result[b])
        val_c = key_fn(result[c])
        if (val_a <= val_b <= val_c) or (val_c <= val_b <= val_a):
            return b
        elif (val_b <= val_a <= val_c) or (val_c <= val_a <= val_b):
            return a
        else:
            return c

    def _partition(low: int, high: int) -> int:
        mid = (low + high) // 2
        pivot_idx = _median_of_three(low, mid, high)
        result[pivot_idx], result[high] = result[high], result[pivot_idx]

        pivot_val = key_fn(result[high])
        i = low - 1

        for j in range(low, high):
            val_j = key_fn(result[j])
            condition = (val_j <= pivot_val) if ascending else (val_j >= pivot_val)
            if condition:
                i += 1
                result[i], result[j] = result[j], result[i]

        result[i + 1], result[high] = result[high], result[i + 1]
        return i + 1

    # Iterative / stack-based quicksort to avoid Python call stack depth limit on massive lists
    stack = [(0, n - 1)]
    while stack:
        low, high = stack.pop()
        if low < high:
            pi = _partition(low, high)
            # Push smaller subarray first to bound auxiliary stack depth to O(log n)
            if (pi - 1 - low) < (high - (pi + 1)):
                stack.append((pi + 1, high))
                stack.append((low, pi - 1))
            else:
                stack.append((low, pi - 1))
                stack.append((pi + 1, high))

    return result
