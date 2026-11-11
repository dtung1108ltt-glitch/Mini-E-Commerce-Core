"""
Python API Layer (FastAPI) for Mini E-Commerce System
A thin HTTP bridge exposing the pure Python DSA core to the UI layer.
Rule: Contains ZERO data-structure logic; delegates exclusively to Core Services.
All timing is measured strictly inside the Python core using time.perf_counter().
"""
import os
import sys
import time
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.product import Product
from src.core.memory_manager import MemoryProfiler
from src.modules.module1_catalog.inventory_service import InventoryService
from src.modules.module2_cart.cart_service import CartService
from src.modules.module3_tree.tree_index_service import TreeIndexService
from src.modules.module4_sort_filter.sort_service import SortFilterService
from src.modules.module5_search.search_service import SearchService

# Singleton service instances in memory
CSV_PATH = os.path.join(BASE_DIR, "data", "products_100k.csv")
inventory_service = InventoryService()
cart_service = CartService(inventory_service)
tree_service = TreeIndexService(inventory_service)
sort_service = SortFilterService(inventory_service)
search_service = SearchService(inventory_service, tree_service)
profiler = MemoryProfiler.get_instance()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load dataset on startup in background
    if os.path.exists(CSV_PATH) and len(inventory_service.catalog) == 0:
        inventory_service.load_from_csv(CSV_PATH, limit=100000)
        tree_service.build_indexes(max_items=10000)
        search_service.build_hash_index(max_items=25000)
    yield

app = FastAPI(
    title="Mini E-Commerce DSA Core API",
    description="Thin FastAPI bridge exposing Python Data Structures & Algorithms",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for local web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= SCHEMAS =================
class ProductCreateSchema(BaseModel):
    id: int = Field(..., gt=0, description="Product unique ID")
    name: str = Field(..., min_length=2, max_length=150, description="Product Name")
    price: float = Field(..., gt=0, description="Unit Price in VND")
    stock: int = Field(..., ge=0, description="Stock quantity")
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating from 1.0 to 5.0")
    position: str = Field("tail", description="'head' or 'tail'")


class CartItemAddSchema(BaseModel):
    product_id: Optional[int] = None
    id: Optional[int] = None
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    quantity: int = Field(1, gt=0)


class CartItemRemoveSchema(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None


class CheckoutOrderSchema(BaseModel):
    customer_name: Optional[str] = "Nguyen Van A"
    customerName: Optional[str] = None


class FilterRequestSchema(BaseModel):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    in_stock_only: bool = False
    in_stock: Optional[bool] = None


class SortBenchmarkRequestSchema(BaseModel):
    sample_size: Optional[int] = None
    sample: Optional[int] = None
    sort_key: Optional[str] = "price"
    by: Optional[str] = None
    ascending: bool = True


# ================= 1. DASHBOARD & SYSTEM STATUS =================
@app.get("/api/system/status")
def get_system_status():
    mem = profiler.get_memory_summary()
    return {
        "catalog_size": len(inventory_service.catalog),
        "cart_size": len(cart_service.cart_items),
        "undo_stack_size": len(cart_service.undo_stack),
        "checkout_queue_size": len(cart_service.checkout_queue),
        "bst_indexed": len(tree_service.bst),
        "avl_indexed": len(tree_service.avl),
        "hash_table_indexed": len(search_service.hash_table),
        "memory_mb": mem["current_mb"],
        "peak_memory_mb": mem["peak_mb"]
    }


# ================= 2. MODULE 1: INVENTORY & CATALOG =================
@app.get("/api/catalog")
def get_catalog_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    pageSize: Optional[int] = Query(None)
):
    """Paginated catalog retrieval. Never sends all 100,000 items to client."""
    if pageSize is not None:
        page_size = pageSize
    return inventory_service.get_page(page=page, page_size=page_size)


@app.post("/api/catalog/product", status_code=status.HTTP_201_CREATED)
@app.post("/api/catalog/add", status_code=status.HTTP_201_CREATED)
def add_product(payload: ProductCreateSchema):
    # Check for duplicate ID
    if inventory_service.get_product_by_id(payload.id):
        raise HTTPException(status_code=400, detail=f"Product with ID {payload.id} already exists.")
    prod = Product(payload.id, payload.name, payload.price, payload.stock, payload.rating)
    inventory_service.add_product(prod, position=payload.position)
    return {"success": True, "product": prod.to_dict(), "position": payload.position}


@app.delete("/api/catalog/product/{product_id}")
@app.delete("/api/catalog/{product_id}")
def delete_product(product_id: int):
    deleted = inventory_service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
    return {"success": True, "deleted": deleted.to_dict()}


@app.post("/api/catalog/cleanup")
def explicit_memory_cleanup():
    """Explicitly releases all linked list nodes and triggers gc.collect()."""
    res = inventory_service.cleanup_inventory()
    # Re-link empty structures
    tree_service.bst.clear()
    tree_service.avl.clear()
    search_service.hash_table.clear()
    return res


@app.post("/api/catalog/reload")
def reload_catalog(limit: int = Query(100000, ge=100, le=100000)):
    if not os.path.exists(CSV_PATH):
        from data.generate_mock_data import generate_mock_csv
        generate_mock_csv(CSV_PATH, 100000)
    count, sec = inventory_service.load_from_csv(CSV_PATH, limit=limit)
    tree_service.build_indexes(max_items=min(count, 10000))
    search_service.build_hash_index(max_items=min(count, 25000))
    return {"success": True, "loaded_count": count, "elapsed_seconds": round(sec, 3)}


# ================= 3. MODULE 2: CART & CHECKOUT =================
@app.get("/api/cart")
def get_cart():
    summary = cart_service.get_cart_summary()
    top_undo = cart_service.undo_stack.peek()
    return {
        **summary,
        "items": summary["items"],
        "totalAmount": summary["total_amount"],
        "totalItems": summary["total_items"],
        "undoStackSize": len(cart_service.undo_stack),
        "undoHistory": [
            {
                "action": "remove",
                "item": {
                    "id": x["product"].id,
                    "name": x["product"].name,
                    "price": x["product"].price,
                    "quantity": x["quantity"],
                    "stock": x["product"].stock,
                },
                "timestamp": time.strftime("%H:%M:%S", time.localtime(x["timestamp"]))
            }
            for x in cart_service.undo_stack.to_list()[:5]
        ],
        "undo_top": {
            "product_id": top_undo["product"].id,
            "product_name": top_undo["product"].name,
            "quantity": top_undo["quantity"]
        } if top_undo else None,
        "undo_stack_items": [
            {
                "product_id": x["product"].id,
                "product_name": x["product"].name,
                "quantity": x["quantity"],
                "timestamp": time.strftime("%H:%M:%S", time.localtime(x["timestamp"]))
            }
            for x in cart_service.undo_stack.to_list()[:10]
        ]
    }


@app.post("/api/cart/add")
def add_to_cart(payload: CartItemAddSchema):
    target_id = payload.product_id if payload.product_id is not None else payload.id
    if target_id is None:
        raise HTTPException(status_code=400, detail="Missing product_id or id in request.")
    success = cart_service.add_to_cart(target_id, payload.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot add to cart: Product not found or insufficient stock.")
    return {"success": True, "cart_size": len(cart_service.cart_items), "cartSize": len(cart_service.cart_items)}


@app.post("/api/cart/remove")
def remove_from_cart(product_id: Optional[int] = Query(None), payload: Optional[CartItemRemoveSchema] = None):
    target_id = product_id
    if target_id is None and payload is not None:
        target_id = payload.product_id if payload.product_id is not None else payload.id
    if target_id is None:
        raise HTTPException(status_code=400, detail="Missing product_id or id.")
    removed = cart_service.remove_from_cart(target_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Product not in cart.")
    return {
        "success": True,
        "removed_product": removed.product.to_dict(),
        "quantity": removed.quantity,
        "undo_stack_size": len(cart_service.undo_stack),
        "undoStackSize": len(cart_service.undo_stack)
    }


@app.post("/api/cart/undo")
def undo_cart_remove():
    restored = cart_service.undo_remove()
    if not restored:
        raise HTTPException(status_code=400, detail="Undo stack is empty.")
    return {"success": True, "restored": restored}


@app.post("/api/checkout/enqueue")
@app.post("/api/checkout/submit-order")
def enqueue_checkout_order(payload: CheckoutOrderSchema):
    if len(cart_service.cart_items) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty. Add products before submitting order.")
    cust_name = payload.customerName or payload.customer_name or "Nguyen Van A"
    order_id = cart_service.submit_order(cust_name)
    return {
        "success": True,
        "order_id": order_id,
        "orderId": order_id,
        "queue_size": len(cart_service.checkout_queue),
        "queueLength": len(cart_service.checkout_queue)
    }


@app.post("/api/checkout/process-next")
def process_next_flash_sale_order():
    log = cart_service.process_next_order()
    if not log:
        return {"message": "Queue is empty", "log": None}
    return {
        "success": True,
        "log": log,
        "remaining_queue": len(cart_service.checkout_queue),
        "remainingQueue": len(cart_service.checkout_queue)
    }


@app.post("/api/checkout/process-all")
def process_all_flash_sale_orders():
    logs = cart_service.process_all_orders()
    return {"success": True, "processed_count": len(logs), "logs": logs}


@app.get("/api/checkout/status")
def get_checkout_status():
    stat = cart_service.get_queue_status()
    # Format queue and logs for frontend
    formatted_queue = [
        {
            "order_id": o.get("order_id", ""),
            "customer_name": o.get("customer_name", "Customer"),
            "total": sum(it["product"].price * it["quantity"] for it in o.get("items", [])),
            "total_amount": sum(it["product"].price * it["quantity"] for it in o.get("items", [])),
            "item_count": len(o.get("items", [])),
            "items": [
                {
                    "id": it["product"].id,
                    "name": it["product"].name,
                    "price": it["product"].price,
                    "quantity": it["quantity"],
                    "stock": it["product"].stock
                }
                for it in o.get("items", [])
            ],
            "timestamp": time.strftime("%H:%M:%S", time.localtime(o.get("timestamp", time.time())))
        }
        for o in cart_service.checkout_queue.to_list()
    ]
    formatted_logs = [
        {
            "order_id": l.get("order_id", ""),
            "customer": l.get("customer", l.get("customer_name", "Customer")),
            "status": l.get("status", "SUCCESS"),
            "amount": l.get("amount", 0.0),
            "detail": l.get("detail", l.get("message", "")),
            "timestamp": l.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        }
        for l in cart_service.processing_logs[-30:]
    ]
    return {
        **stat,
        "queue": formatted_queue,
        "queueLength": len(formatted_queue),
        "logs": formatted_logs
    }


# ================= 4. MODULE 3: BST & AVL TREES =================
@app.get("/api/tree/stats")
def get_tree_stats(count: int = Query(10000, ge=100, le=50000)):
    return tree_service.build_indexes(max_items=count)


@app.get("/api/tree/search/{product_id}")
def search_tree_by_id(product_id: int):
    res = tree_service.search_by_id(product_id)
    if not res["found"]:
        raise HTTPException(status_code=404, detail=f"Product ID {product_id} not found in tree index.")
    return res


@app.get("/api/tree/traversal")
def get_tree_traversal(
    tree_type: str = Query("bst", pattern="^(bst|avl)$"),
    traversal: str = Query("in_order", pattern="^(in_order|pre_order|post_order)$"),
    limit: int = Query(15, ge=1, le=50)
):
    items = tree_service.get_traversals(tree_type=tree_type, traversal=traversal, limit=limit)
    return {"tree_type": tree_type, "traversal": traversal, "count": len(items), "items": items}


@app.get("/api/tree/visualize")
def get_tree_visual_subtree(root_limit_depth: int = Query(4, ge=1, le=6)):
    """
    Returns visual JSON tree hierarchy up to N levels (since 100k nodes cannot be rendered in browser).
    """
    def serialize_node(node, depth, max_d):
        if not node or depth > max_d:
            return None
        return {
            "id": node.key,
            "name": node.product.name[:20],
            "price": node.product.price,
            "height": getattr(node, "height", None),
            "left": serialize_node(node.left, depth + 1, max_d),
            "right": serialize_node(node.right, depth + 1, max_d)
        }

    return {
        "bst": serialize_node(tree_service.bst.root, 1, root_limit_depth),
        "avl": serialize_node(tree_service.avl.root, 1, root_limit_depth),
        "bst_height": tree_service.bst.height(),
        "avl_height": tree_service.avl.height(),
        "avl_rotations": tree_service.avl.rotations_count
    }


@app.get("/api/tree/degeneration-demo")
def tree_degeneration_demo():
    """Demo on sorted input showing naive BST degeneration vs AVL height balance."""
    from src.modules.module3_tree.bst import BinarySearchTree
    from src.modules.module3_tree.avl import AVLTree
    
    test_sizes = [50, 100, 200, 500, 1000]
    results = []
    for n in test_sizes:
        bst = BinarySearchTree()
        avl = AVLTree()
        for i in range(1, n + 1):
            p = Product(i, f"Product #{i}", 100000, 10, 4.5)
            bst.insert(p)
            avl.insert(p)

        t0 = time.perf_counter_ns()
        bst.search(n)
        bst_ns = time.perf_counter_ns() - t0

        t0 = time.perf_counter_ns()
        avl.search(n)
        avl_ns = time.perf_counter_ns() - t0

        results.append({
            "n": n,
            "bst_height": bst.height(),
            "bst_search_ns": bst_ns,
            "avl_height": avl.height(),
            "avl_rotations": avl.rotations_count,
            "avl_search_ns": avl_ns
        })
    return {"demo_input": "Strictly ascending sorted IDs [1..N]", "results": results}


# ================= 5. MODULE 4: SORTING & FILTERING =================
@app.post("/api/sort/benchmark")
def run_sort_benchmark(payload: SortBenchmarkRequestSchema):
    """
    Runs head-to-head sorting benchmark measured strictly inside Python core with perf_counter.
    """
    sample_size = payload.sample_size if payload.sample_size is not None else (payload.sample or 5000)
    by = payload.by or payload.sort_key or "price"
    return sort_service.run_sort_benchmark(
        sample_size=sample_size,
        by=by,
        ascending=payload.ascending
    )


@app.post("/api/sort/filter")
def filter_catalog(payload: FilterRequestSchema):
    in_stock = payload.in_stock if payload.in_stock is not None else payload.in_stock_only
    filtered = sort_service.filter_catalog(
        min_price=payload.min_price,
        max_price=payload.max_price,
        min_rating=payload.min_rating,
        max_rating=payload.max_rating,
        in_stock_only=in_stock
    )
    return {
        "total_matched": len(filtered),
        "items": [p.to_dict() for p in filtered[:50]]
    }


@app.get("/api/sort/step-demo")
def get_sort_step_animation_data(algorithm: str = Query("bubble", pattern="^(bubble|insertion|selection|quick|merge)$"), n: int = Query(12, ge=5, le=25)):
    """
    Returns step-by-step sorting trace for small educational animations (12 elements).
    Labeled strictly as educational illustration.
    """
    import random
    random.seed(123)
    initial_values = [random.randint(10, 99) for _ in range(n)]
    steps = [{"arr": list(initial_values), "comparing": [], "swapped": []}]

    arr = list(initial_values)
    if algorithm == "bubble":
        for i in range(len(arr)):
            for j in range(0, len(arr) - i - 1):
                steps.append({"arr": list(arr), "comparing": [j, j + 1], "swapped": []})
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    steps.append({"arr": list(arr), "comparing": [], "swapped": [j, j + 1]})
    elif algorithm == "selection":
        for i in range(len(arr)):
            min_idx = i
            for j in range(i + 1, len(arr)):
                steps.append({"arr": list(arr), "comparing": [min_idx, j], "swapped": []})
                if arr[j] < arr[min_idx]:
                    min_idx = j
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                steps.append({"arr": list(arr), "comparing": [], "swapped": [i, min_idx]})
    elif algorithm == "insertion":
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                steps.append({"arr": list(arr), "comparing": [j, j + 1], "swapped": []})
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
            steps.append({"arr": list(arr), "comparing": [], "swapped": [j + 1]})

    return {
        "algorithm": algorithm,
        "n": n,
        "total_steps": len(steps),
        "steps": steps,
        "note": "Minh họa sư phạm trên tập nhỏ (Educational Illustration Only)"
    }


# ================= 6. MODULE 5: SEARCH & HISTORY =================
@app.get("/api/search/hash")
@app.get("/api/search/name")
def search_product_by_name(q: Optional[str] = Query(None), query: Optional[str] = Query(None)):
    search_q = q or query or ""
    res = search_service.search_by_name_hash(search_q)
    return res


@app.get("/api/search/compare/{product_id}")
@app.get("/api/search/compare")
def compare_search_algorithms(product_id: Optional[int] = None, id: Optional[int] = Query(None)):
    target_id = product_id if product_id is not None else (id or 1000)
    return search_service.compare_search_methods_by_id(target_id)


@app.get("/api/search/hash-inspector")
def get_hash_table_inspector():
    """Inspects Hash Table buckets, collisions, and load factor."""
    stats = search_service.hash_table.get_statistics()
    bucket_lengths = []
    for idx in range(min(50, search_service.hash_table._capacity)):
        head = search_service.hash_table._buckets[idx]
        count = 0
        curr = head
        while curr:
            count += 1
            curr = curr.next
        bucket_lengths.append({"bucket_index": idx, "chain_length": count})
    return {
        "stats": stats,
        "bucket_sample": bucket_lengths
    }


@app.get("/api/search/history")
def get_search_history(strategy: str = Query("MTF", pattern="^(MTF|Transpose|TRANSPOSE)$")):
    return search_service.get_search_history(strategy=strategy)


# ================= 7. BENCHMARKS & PLOTS =================
@app.get("/api/benchmark/plots")
@app.get("/api/benchmark/charts")
def get_benchmark_plots():
    plots_dir = os.path.join(BASE_DIR, "benchmark", "plots")
    results = []
    chart_info = [
        ("chart_sorting_benchmark.png", "So sánh thuật toán sắp xếp O(n²) vs O(n log n)", "benchmark_sorting.csv"),
        ("chart_search_benchmark.png", "Độ trễ tra cứu: Linear vs Binary vs BST vs Hash (Thang Log)", "benchmark_search.csv"),
        ("chart_tree_degeneration.png", "Hiện tượng thoái hóa cây: BST vs AVL trên dữ liệu sắp xếp", "benchmark_bst_avl.csv"),
        ("chart_self_organizing.png", "Hiệu quả thăm dò: Move-to-Front vs Transpose (Phân phối Zipf)", "benchmark_self_organizing.csv"),
        ("chart_memory_profiling.png", "Vòng đời tiêu thụ RAM (Baseline, 100k items, Cleanup)", "benchmark_memory.csv"),
    ]
    for fn, label, csv_fn in chart_info:
        p = os.path.join(plots_dir, fn)
        results.append({
            "filename": fn,
            "title": label,
            "exists": os.path.exists(p),
            "csv_file": csv_fn,
            "url": f"/plots/{fn}"
        })
    return {"charts": results}


@app.post("/api/benchmark/run")
def trigger_benchmark_execution():
    script_path = os.path.join(BASE_DIR, "benchmark", "run_all_benchmarks.py")
    t0 = time.perf_counter()
    ret = os.system(f"python3 \"{script_path}\"")
    elapsed = time.perf_counter() - t0
    if ret != 0:
        raise HTTPException(status_code=500, detail="Benchmark execution failed")
    return {"success": True, "elapsed_seconds": round(elapsed, 2)}


# ================= 8. MEMORY PROFILING =================
@app.get("/api/memory/profile")
def get_memory_profile():
    return profiler.get_memory_summary()


# ================= 9. REPORT DOWNLOAD =================
@app.get("/api/report/download")
def download_academic_report():
    doc_path = os.path.join(BASE_DIR, "report", "BCTieuLuan_CTDL_GT_Nhom.docx")
    if not os.path.exists(doc_path):
        # Auto compile
        from report.generate_term_paper import build_academic_report
        build_academic_report()
    return FileResponse(
        doc_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="BCTieuLuan_CTDL_GT_Nhom.docx"
    )


@app.post("/api/report/generate")
def recompile_academic_report():
    from report.generate_term_paper import build_academic_report
    build_academic_report()
    return {"success": True, "path": "report/BCTieuLuan_CTDL_GT_Nhom.docx"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
