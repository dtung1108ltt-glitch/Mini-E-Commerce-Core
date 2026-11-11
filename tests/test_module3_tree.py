"""
Tests for Module 3: High-speed Index (BST & AVL Trees)
"""
import pytest
from src.core.product import Product
from src.modules.module3_tree.bst import BinarySearchTree
from src.modules.module3_tree.avl import AVLTree


def test_bst_operations_and_traversals():
    bst = BinarySearchTree()
    assert bst.is_empty()

    # Insert in specific order
    ids = [50, 30, 70, 20, 40, 60, 80]
    for pid in ids:
        bst.insert(Product(pid, f"Prod {pid}", pid * 1000, 10, 4.5))

    assert len(bst) == 7

    # Search
    found = bst.search(40)
    assert found is not None
    assert found.name == "Prod 40"
    assert bst.search(999) is None

    # Traversals
    in_order_ids = [p.id for p in bst.in_order()]
    assert in_order_ids == [20, 30, 40, 50, 60, 70, 80]

    pre_order_ids = [p.id for p in bst.pre_order()]
    assert pre_order_ids == [50, 30, 20, 40, 70, 60, 80]

    post_order_ids = [p.id for p in bst.post_order()]
    assert post_order_ids == [20, 40, 30, 60, 80, 70, 50]

    # Deletion (two children: 50 root)
    deleted = bst.delete(50)
    assert deleted is not None
    assert deleted.id == 50
    assert len(bst) == 6
    assert [p.id for p in bst.in_order()] == [20, 30, 40, 60, 70, 80]


def test_avl_rotations_and_balance_invariant():
    avl = AVLTree()

    # Insert strictly ascending numbers: naive BST would degenerate to height 7
    # AVL will rotate and keep height balanced
    for i in [10, 20, 30, 40, 50, 60, 70]:
        avl.insert(Product(i, f"Prod {i}", i * 1000, 10, 4.5))

    assert len(avl) == 7
    assert avl.rotations_count > 0
    # AVL height for 7 nodes should be 3
    assert avl.height() == 3

    # Check search
    assert avl.search(40) is not None
    assert avl.search(999) is None

    # In-order should be sorted
    assert [p.id for p in avl.in_order()] == [10, 20, 30, 40, 50, 60, 70]

    # Deletion with rebalancing
    del_p = avl.delete(40)
    assert del_p is not None
    assert len(avl) == 6
    assert avl.height() <= 4
