"""
API Layer Tests (FastAPI TestClient)
Verifies that the Python API properly exposes the Core DSA modules, enforces validation,
and adheres to server-side pagination constraints without shortcutting DSA logic.
"""
import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_system_status():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "catalog_size" in data
    assert "memory_mb" in data
    assert data["catalog_size"] >= 0


def test_catalog_pagination_and_validation():
    # Test valid pagination
    response = client.get("/api/catalog?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) <= 10

    # Test invalid page size (> 100 limit)
    res_invalid = client.get("/api/catalog?page=1&page_size=500")
    assert res_invalid.status_code == 422  # Validation error


def test_product_creation_and_validation():
    # Valid product addition
    valid_payload = {
        "id": 888888,
        "name": "Test Mechanical Keyboard",
        "price": 1200000.0,
        "stock": 15,
        "rating": 4.7,
        "position": "tail"
    }
    res = client.post("/api/catalog/product", json=valid_payload)
    assert res.status_code == 201
    assert res.json()["success"] is True

    # Duplicate ID rejection
    res_dup = client.post("/api/catalog/product", json=valid_payload)
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"]

    # Invalid rating (> 5.0)
    invalid_payload = {**valid_payload, "id": 888889, "rating": 6.5}
    res_inv = client.post("/api/catalog/product", json=invalid_payload)
    assert res_inv.status_code == 422

    # Cleanup added product
    client.delete(f"/api/catalog/product/888888")


def test_cart_and_undo_flow():
    # Ensure test product exists in inventory
    prod_id = 999991
    client.post("/api/catalog/product", json={
        "id": prod_id,
        "name": "Cart Test Item",
        "price": 50000,
        "stock": 10,
        "rating": 4.5,
        "position": "head"
    })

    # Add to cart
    res_add = client.post("/api/cart/add", json={"product_id": prod_id, "quantity": 1})
    assert res_add.status_code == 200

    # Inspect cart
    res_cart = client.get("/api/cart")
    assert res_cart.status_code == 200
    assert res_cart.json()["total_items"] >= 1

    # Remove from cart (pushes to undo stack)
    res_rem = client.post(f"/api/cart/remove?product_id={prod_id}")
    assert res_rem.status_code == 200
    assert res_rem.json()["undo_stack_size"] >= 1

    # Undo removal
    res_undo = client.post("/api/cart/undo")
    assert res_undo.status_code == 200
    assert res_undo.json()["restored"]["restored_product_id"] == prod_id



def test_tree_and_traversal_endpoints():
    res_stats = client.get("/api/tree/stats?count=500")
    assert res_stats.status_code == 200
    data = res_stats.json()
    assert "bst" in data
    assert "avl" in data
    assert data["avl"]["height"] <= 12  # Strictly balanced

    res_trav = client.get("/api/tree/traversal?tree_type=bst&traversal=in_order&limit=5")
    assert res_trav.status_code == 200
    assert len(res_trav.json()["items"]) <= 5


def test_search_and_hash_inspector():
    # Hash search
    res_search = client.get("/api/search/hash?q=NonexistentProductXYZ")
    assert res_search.status_code == 200
    assert res_search.json()["found"] is False

    # Inspector
    res_inspect = client.get("/api/search/hash-inspector")
    assert res_inspect.status_code == 200
    assert "stats" in res_inspect.json()
    assert "bucket_sample" in res_inspect.json()
