"""
API Bridge for Mini E-Commerce System
Provides CLI-to-JSON interface for Express server endpoints to query the Python DSA engine.
"""
import os
import sys
import json

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.product import Product
from src.core.memory_manager import MemoryProfiler
from src.modules.module1_catalog.inventory_service import InventoryService
from src.modules.module2_cart.cart_service import CartService
from src.modules.module3_tree.tree_index_service import TreeIndexService
from src.modules.module4_sort_filter.sort_service import SortFilterService
from src.modules.module5_search.search_service import SearchService

# Persistent state file for web sessions
STATE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "web_state.json"))
CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "products_100k.csv"))


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "cart": {},
        "undo_stack": [],
        "checkout_queue": [],
        "logs": [],
        "history_mtf": [],
        "history_trans": []
    }


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        return

    action = sys.argv[1]
    args = {}
    if len(sys.argv) > 2:
        try:
            args = json.loads(sys.argv[2])
        except Exception:
            pass

    inv_svc = InventoryService()
    # Check if CSV exists, if not generate small one
    if not os.path.exists(CSV_FILE):
        from data.generate_mock_data import generate_mock_csv
        generate_mock_csv(CSV_FILE, 100000)

    # For API speed on ad-hoc commands, load up to 25,000 items into memory
    limit = args.get("limit", 25000)
    inv_svc.load_from_csv(CSV_FILE, limit=limit)

    tree_svc = TreeIndexService(inv_svc)
    sort_svc = SortFilterService(inv_svc)
    search_svc = SearchService(inv_svc, tree_svc)

    response = {}

    if action == "get_catalog":
        page = int(args.get("page", 1))
        page_size = int(args.get("page_size", 20))
        response = inv_svc.get_page(page, page_size)

    elif action == "add_product":
        p = Product(
            product_id=int(args["id"]),
            name=args["name"],
            price=float(args["price"]),
            stock=int(args["stock"]),
            rating=float(args["rating"])
        )
        pos = args.get("position", "tail")
        inv_svc.add_product(p, position=pos)
        response = {"success": True, "product": p.to_dict(), "position": pos}

    elif action == "delete_product":
        pid = int(args["id"])
        deleted = inv_svc.delete_product(pid)
        response = {"success": deleted is not None, "deleted": deleted.to_dict() if deleted else None}

    elif action == "sort_catalog":
        by = args.get("by", "price")
        asc = args.get("ascending", True)
        sample = int(args.get("sample", 5000))
        res = sort_svc.run_sort_benchmark(sample_size=sample, by=by, ascending=asc)
        response = res

    elif action == "filter_catalog":
        min_p = args.get("min_price")
        max_p = args.get("max_price")
        min_r = args.get("min_rating")
        in_stock = args.get("in_stock", False)
        filtered = sort_svc.filter_catalog(min_price=min_p, max_price=max_p, min_rating=min_r, in_stock_only=in_stock)
        response = {
            "total_found": len(filtered),
            "items": [p.to_dict() for p in filtered[:50]]
        }

    elif action == "search_name":
        query = args.get("query", "")
        search_svc.build_hash_index(max_items=15000)
        res = search_svc.search_by_name_hash(query)
        response = res

    elif action == "compare_search":
        pid = int(args.get("id", 1000))
        tree_svc.build_indexes(max_items=10000)
        res = search_svc.compare_search_methods_by_id(pid)
        response = res

    elif action == "tree_stats":
        stats = tree_svc.build_indexes(max_items=int(args.get("count", 10000)))
        response = stats

    elif action == "tree_traversal":
        tree_svc.build_indexes(max_items=5000)
        trav = args.get("traversal", "in_order")
        items = tree_svc.get_traversals(tree_type=args.get("tree_type", "bst"), traversal=trav, limit=int(args.get("limit", 20)))
        response = {"traversal": trav, "items": items}

    elif action == "memory_cleanup":
        res = inv_svc.cleanup_inventory()
        response = res

    else:
        response = {"error": f"Unknown action '{action}'"}

    print(json.dumps(response))


if __name__ == "__main__":
    main()
