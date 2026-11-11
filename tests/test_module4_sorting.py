"""
Tests for Module 4: Filter & Sorting Engine
"""
import pytest
from src.core.product import Product
from src.modules.module4_sort_filter.filters import ProductFilter
from src.modules.module4_sort_filter.basic_sorts import bubble_sort, selection_sort, insertion_sort
from src.modules.module4_sort_filter.advanced_sorts import merge_sort, quick_sort


@pytest.fixture
def sample_products():
    return [
        Product(101, "Phone A", 5000000, 10, 4.2),
        Product(102, "Phone B", 12000000, 5, 4.8),
        Product(103, "Earbuds C", 800000, 0, 3.9),
        Product(104, "Laptop D", 25000000, 2, 4.9),
        Product(105, "Mouse E", 350000, 20, 4.5),
    ]


def test_product_filters(sample_products):
    # Price filter
    price_filtered = ProductFilter.filter_by_price(sample_products, min_price=500000, max_price=10000000)
    assert [p.id for p in price_filtered] == [101, 103]

    # Rating filter
    rating_filtered = ProductFilter.filter_by_rating(sample_products, min_rating=4.5)
    assert [p.id for p in rating_filtered] == [102, 104, 105]

    # Combined with in-stock
    combined = ProductFilter.filter_combined(
        sample_products, min_price=300000, max_price=30000000, min_rating=4.0, in_stock_only=True
    )
    # Earbuds C is stock=0, so excluded
    assert len(combined) == 4
    assert 103 not in [p.id for p in combined]


def test_sorting_algorithms(sample_products):
    # Sort by price ascending
    expected_ids_asc = [105, 103, 101, 102, 104]
    expected_ids_desc = [104, 102, 101, 103, 105]

    for sort_fn in [bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort]:
        # Ascending
        res_asc = sort_fn(sample_products, by="price", ascending=True)
        assert [p.id for p in res_asc] == expected_ids_asc

        # Descending
        res_desc = sort_fn(sample_products, by="price", ascending=False)
        assert [p.id for p in res_desc] == expected_ids_desc


def test_sorting_edge_cases():
    # Empty and single-element lists
    empty = []
    single = [Product(1, "Solo", 1000, 1, 5.0)]

    for sort_fn in [merge_sort, quick_sort]:
        assert sort_fn(empty, by="price") == []
        assert len(sort_fn(single, by="price")) == 1

    # Already sorted list (tests QuickSort median-of-three against worst-case)
    sorted_input = [Product(i, f"P{i}", i * 1000, 1, 4.0) for i in range(1, 50)]
    qs_res = quick_sort(sorted_input, by="price", ascending=True)
    assert [p.id for p in qs_res] == list(range(1, 50))
