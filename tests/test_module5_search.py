"""
Tests for Module 5: Instant Search & Search History
"""
import pytest
from src.core.product import Product
from src.modules.module5_search.hash_table import HashTable
from src.modules.module5_search.self_organizing_list import SelfOrganizingList
from src.modules.module5_search.linear_binary_search import (
    linear_search_by_id,
    linear_search_by_name,
    binary_search_by_id
)


def test_hash_table_operations_and_rehashing():
    # Use small capacity to trigger rehashing quickly
    ht = HashTable(initial_capacity=7, load_factor_threshold=0.7)

    products = [
        Product(i, f"Product Name #{i}", i * 10000, 10, 4.0)
        for i in range(1, 20)
    ]

    for p in products:
        ht.insert(p.name, p)

    assert len(ht) == 19
    # Must have triggered rehash
    assert ht.rehash_count > 0

    # Search
    found = ht.search("Product Name #5")
    assert found is not None
    assert found.id == 5

    assert ht.search("Nonexistent Product") is None

    # Delete
    deleted = ht.delete("Product Name #5")
    assert deleted is not None
    assert deleted.id == 5
    assert len(ht) == 18
    assert ht.search("Product Name #5") is None

    # Check stats
    stats = ht.get_statistics()
    assert stats["load_factor"] <= 0.75
    assert stats["total_items"] == 18


def test_self_organizing_list_mtf_vs_transpose():
    # Move-to-Front (MTF)
    mtf = SelfOrganizingList(strategy="MTF")
    mtf.record_search("laptop")
    mtf.record_search("phone")
    mtf.record_search("headphones")
    # Order: headphones -> phone -> laptop

    # Access "laptop" again -> should move directly to head
    probes = mtf.record_search("laptop")
    assert probes == 3  # was at position 3
    assert mtf.head.keyword == "laptop"

    # Transpose
    trans = SelfOrganizingList(strategy="Transpose")
    trans.record_search("laptop")
    trans.record_search("phone")
    trans.record_search("headphones")
    # Order: headphones -> phone -> laptop

    # Access "laptop" again -> should swap with predecessor "phone"
    # New order: headphones -> laptop -> phone
    probes_t = trans.record_search("laptop")
    assert probes_t == 3
    assert trans.head.keyword == "headphones"
    assert trans.head.next.keyword == "laptop"
    assert trans.head.next.next.keyword == "phone"


def test_linear_and_binary_search():
    prods = [Product(i, f"P{i}", i * 1000, 5, 4.0) for i in [10, 20, 30, 40, 50]]

    # Linear search
    p_lin, comps_lin = linear_search_by_id(prods, 30)
    assert p_lin is not None
    assert p_lin.id == 30
    assert comps_lin == 3

    # Binary search
    p_bin, comps_bin = binary_search_by_id(prods, 30)
    assert p_bin is not None
    assert p_bin.id == 30
    assert comps_bin <= 3  # log2(5) is < 3
