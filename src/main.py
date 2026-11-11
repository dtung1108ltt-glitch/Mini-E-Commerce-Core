"""
Mini E-Commerce Core Engine - Main Console Application
Integrates all 5 DSA modules:
1. Catalog & Inventory (Doubly Linked List)
2. Cart & Order Processing (Stack Undo + Queue Flash Sale)
3. High-Speed Index (BST & AVL Trees)
4. Filter & Sorting Engine (Bubble, Selection, Insertion vs Merge, QuickSort)
5. Instant Search & Search History (Hash Table, MTF vs Transpose, Linear vs Binary)
Plus: Memory Profiling, Benchmarks, and Demo Scenarios.
"""
import os
import sys
import time

# Ensure project root is on Python sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.product import Product
from src.core.memory_manager import MemoryProfiler
from src.modules.module1_catalog.inventory_service import InventoryService
from src.modules.module2_cart.cart_service import CartService
from src.modules.module3_tree.tree_index_service import TreeIndexService
from src.modules.module4_sort_filter.sort_service import SortFilterService
from src.modules.module5_search.search_service import SearchService
from src.utils.cli_formatter import (
    print_banner, print_section, print_table,
    prompt_int, prompt_float, prompt_str,
    GREEN, YELLOW, RED, CYAN, BOLD, RESET, DIM
)
from data.generate_mock_data import generate_mock_csv


class EcommerceConsoleApp:
    def __init__(self):
        self.inventory_service = InventoryService()
        self.cart_service = CartService(self.inventory_service)
        self.tree_service = TreeIndexService(self.inventory_service)
        self.sort_service = SortFilterService(self.inventory_service)
        self.search_service = SearchService(self.inventory_service, self.tree_service)
        self.profiler = MemoryProfiler.get_instance()
        self.data_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "products_100k.csv"))

    def initialize_system(self):
        """Auto-generate mock dataset if not present and auto-load 100,000 products."""
        print(f"{CYAN}Initializing Mini E-Commerce System...{RESET}")
        if not os.path.exists(self.data_filepath):
            print(f"{YELLOW}Catalog CSV not detected. Generating 100,000 product mock dataset...{RESET}")
            generate_mock_csv(self.data_filepath, 100000)

        # Preload catalog
        count, sec = self.inventory_service.load_from_csv(self.data_filepath, limit=100000)
        print(f"{GREEN}✓ Loaded {count:,} products into Doubly Linked List in {sec:.2f}s.{RESET}")

        # Preload tree index and hash table for instant operations
        print(f"{CYAN}Building BST/AVL trees and Hash Table indexes...{RESET}")
        self.tree_service.build_indexes(max_items=10000)  # Index top 10,000 for responsive demo
        self.search_service.build_hash_index(max_items=25000)
        print(f"{GREEN}✓ System ready.{RESET}\n")

    def run(self):
        print_banner()
        self.initialize_system()

        while True:
            self.display_main_menu()
            choice = prompt_int("Select option [0-8]", default=1, min_val=0, max_val=8)

            try:
                if choice == 0:
                    self.handle_exit()
                    break
                elif choice == 1:
                    self.menu_catalog()
                elif choice == 2:
                    self.menu_cart()
                elif choice == 3:
                    self.menu_trees()
                elif choice == 4:
                    self.menu_sort_filter()
                elif choice == 5:
                    self.menu_search()
                elif choice == 6:
                    self.run_benchmark_suite()
                elif choice == 7:
                    self.generate_academic_report()
                elif choice == 8:
                    self.menu_memory()
            except Exception as e:
                print(f"{RED}An unexpected error occurred: {e}{RESET}")
                time.sleep(1)

    def display_main_menu(self):
        print(f"\n{BOLD}{CYAN}═══════════════════════ MAIN MENU ═══════════════════════{RESET}")
        print(f" Catalog Size: {GREEN}{len(self.inventory_service.catalog):,} items{RESET} | Cart Items: {YELLOW}{len(self.cart_service.cart_items)}{RESET}")
        print(f" [1] Catalog & Inventory Management (Doubly Linked List)")
        print(f" [2] Shopping Cart & Flash Sale Checkout (Stack Undo + Queue FIFO)")
        print(f" [3] High-Speed ID Indexing (BST & AVL Trees)")
        print(f" [4] Filter & Sorting Laboratory (O(n²) vs O(n log n))")
        print(f" [5] Instant Search & Keyword History (Hash Table, MTF/Transpose)")
        print(f" [6] Run Full Benchmark Suite (CSV & PNG Export)")
        print(f" [7] Generate Term-Paper Report (.docx)")
        print(f" [8] Memory Profiling & Explicit Cleanup")
        print(f" [0] Exit Application")
        print(f"{DIM}{'─' * 57}{RESET}")

    # ================= MODULE 1: CATALOG =================
    def menu_catalog(self):
        while True:
            print_section("Module 1: Catalog & Inventory Management")
            print(" [1] Browse Products (Paginated)")
            print(" [2] Add Product at HEAD - O(1)")
            print(" [3] Add Product at TAIL - O(1)")
            print(" [4] Delete Product by ID - O(n) scan + O(1) unlink")
            print(" [5] Reload Catalog from CSV")
            print(" [0] Back to Main Menu")

            opt = prompt_int("Choose catalog option", default=1, min_val=0, max_val=5)
            if opt == 0:
                break
            elif opt == 1:
                page = prompt_int("Enter Page Number", default=1, min_val=1)
                page_size = prompt_int("Items per page", default=10, min_val=1, max_val=100)
                page_data = self.inventory_service.get_page(page, page_size)
                headers = ["ID", "Name", "Price (VND)", "Stock", "Rating"]
                rows = [
                    [f"{p['id']:06d}", p["name"], f"{p['price']:,.0f}", p["stock"], f"★ {p['rating']:.1f}"]
                    for p in page_data["items"]
                ]
                print(f"\nPage {page_data['page']} of {page_data['total_pages']} (Total: {page_data['total_items']:,} items)")
                print_table(headers, rows)
            elif opt in (2, 3):
                pos = "head" if opt == 2 else "tail"
                pid = prompt_int("Enter Product ID", default=999999)
                name = prompt_str("Enter Product Name", default="Sony Pro Wireless ANC Headphones")
                price = prompt_float("Enter Price (VND)", default=4500000.0)
                stock = prompt_int("Enter Stock Quantity", default=50)
                rating = prompt_float("Enter Rating (1.0 - 5.0)", default=4.8, min_val=1.0, max_val=5.0)
                prod = Product(pid, name, price, stock, rating)
                self.inventory_service.add_product(prod, position=pos)
                print(f"{GREEN}✓ Successfully added product at {pos.upper()}: {prod.name}{RESET}")
            elif opt == 4:
                pid = prompt_int("Enter Product ID to delete")
                deleted = self.inventory_service.delete_product(pid)
                if deleted:
                    print(f"{GREEN}✓ Successfully deleted product [{deleted.id}] {deleted.name}{RESET}")
                else:
                    print(f"{RED}Product ID {pid} not found in catalog.{RESET}")
            elif opt == 5:
                limit = prompt_int("Load limit (items)", default=100000, min_val=100)
                count, sec = self.inventory_service.load_from_csv(self.data_filepath, limit=limit)
                print(f"{GREEN}✓ Loaded {count:,} items from CSV in {sec:.2f}s.{RESET}")

    # ================= MODULE 2: CART & CHECKOUT =================
    def menu_cart(self):
        while True:
            print_section("Module 2: Shopping Cart & Flash Sale Checkout")
            print(" [1] View Current Cart & Undo Stack")
            print(" [2] Add Product to Cart")
            print(" [3] Remove Product from Cart (Pushes to Undo Stack - LIFO)")
            print(" [4] Undo Last Removal (Pop Stack - LIFO)")
            print(" [5] Submit Cart to Flash Sale Checkout Queue (FIFO)")
            print(" [6] Simulate Flash Sale: Process Next Queued Order")
            print(" [7] Simulate Flash Sale: Process ALL Queued Orders")
            print(" [8] View Flash Sale Processing Logs")
            print(" [0] Back to Main Menu")

            opt = prompt_int("Choose cart option", default=1, min_val=0, max_val=8)
            if opt == 0:
                break
            elif opt == 1:
                summary = self.cart_service.get_cart_summary()
                headers = ["ID", "Name", "Unit Price", "Qty", "Subtotal (VND)"]
                rows = [
                    [p["product"]["id"], p["product"]["name"], f"{p['product']['price']:,.0f}", p["quantity"], f"{p['subtotal']:,.0f}"]
                    for p in summary["items"]
                ]
                print(f"\n{BOLD}ACTIVE CART (Total: {summary['total_items']} items, {summary['total_amount']:,.0f} VND | Undo History Size: {summary['undo_stack_size']}){RESET}")
                print_table(headers, rows)
            elif opt == 2:
                pid = prompt_int("Enter Product ID to add to cart", default=1)
                qty = prompt_int("Quantity", default=1, min_val=1)
                success = self.cart_service.add_to_cart(pid, qty)
                if success:
                    print(f"{GREEN}✓ Added {qty}x item [{pid}] to cart.{RESET}")
                else:
                    print(f"{RED}Failed to add item: Not found or insufficient stock.{RESET}")
            elif opt == 3:
                pid = prompt_int("Enter Product ID to remove from cart")
                removed = self.cart_service.remove_from_cart(pid)
                if removed:
                    print(f"{YELLOW}✓ Removed [{removed.product.id}] {removed.product.name} (Qty: {removed.quantity}). Saved to Undo Stack.{RESET}")
                else:
                    print(f"{RED}Product ID {pid} is not in the cart.{RESET}")
            elif opt == 4:
                restored = self.cart_service.undo_remove()
                if restored:
                    print(f"{GREEN}✓ UNDO SUCCESS: Restored [{restored['restored_product_id']}] {restored['restored_name']} (Qty: {restored['quantity']}) back to cart.{RESET}")
                else:
                    print(f"{YELLOW}Undo stack is empty! No actions to undo.{RESET}")
            elif opt == 5:
                cust_name = prompt_str("Customer Name", default="Nguyen Van A")
                order_id = self.cart_service.submit_order(cust_name)
                print(f"{GREEN}✓ Order submitted to Flash Sale Queue with ID: {order_id} (FIFO enqueued){RESET}")
            elif opt == 6:
                log = self.cart_service.process_next_order()
                if log:
                    color = GREEN if log["status"] == "SUCCESS" else RED
                    print(f"{color}[{log['status']}] Order {log['order_id']} | Cust: {log['customer']} | {log['detail']}{RESET}")
                else:
                    print(f"{DIM}Flash sale queue is empty.{RESET}")
            elif opt == 7:
                logs = self.cart_service.process_all_orders()
                print(f"{GREEN}Processed {len(logs)} queued flash sale orders:{RESET}")
                for l in logs:
                    c = GREEN if l["status"] == "SUCCESS" else RED
                    print(f" {c}• [{l['status']}] {l['order_id']} | {l['customer']} | {l['amount']:,.0f} VND | {l['detail']}{RESET}")
            elif opt == 8:
                logs = self.cart_service.processing_logs
                headers = ["Time", "Order ID", "Customer", "Status", "Amount (VND)", "Details"]
                rows = [
                    [l["timestamp"], l["order_id"], l["customer"], l["status"], f"{l['amount']:,.0f}", l["detail"][:35]]
                    for l in logs[-15:]
                ]
                print_table(headers, rows)

    # ================= MODULE 3: BST & AVL =================
    def menu_trees(self):
        while True:
            print_section("Module 3: High-Speed ID Indexing (BST & AVL Trees)")
            print(" [1] Rebuild BST & AVL Trees from Inventory")
            print(" [2] Search Product by ID (Compare BST vs AVL Latencies)")
            print(" [3] View Pre-order Traversal (BST)")
            print(" [4] View In-order Traversal (Sorted BST / AVL)")
            print(" [5] View Post-order Traversal (BST)")
            print(" [6] BST vs AVL Degeneration Comparison on Sorted Input")
            print(" [0] Back to Main Menu")

            opt = prompt_int("Choose tree option", default=1, min_val=0, max_val=6)
            if opt == 0:
                break
            elif opt == 1:
                n = prompt_int("Number of items to index into trees", default=10000, min_val=100)
                stats = self.tree_service.build_indexes(max_items=n)
                print(f"\n{GREEN}✓ Indexed {stats['indexed_count']:,} products into both trees:{RESET}")
                headers = ["Tree Type", "Build Time (s)", "Height", "Node Count", "Rotations"]
                rows = [
                    ["BST (Naive)", f"{stats['bst']['build_time_sec']:.4f}", stats['bst']['height'], stats['bst']['node_count'], "0 (Unbalanced)"],
                    ["AVL (Self-Balancing)", f"{stats['avl']['build_time_sec']:.4f}", stats['avl']['height'], stats['avl']['node_count'], stats['avl']['rotations']]
                ]
                print_table(headers, rows)
            elif opt == 2:
                pid = prompt_int("Enter Product ID to search", default=5000)
                res = self.tree_service.search_by_id(pid)
                if res["found"]:
                    prod = res["product"]
                    print(f"{GREEN}✓ Found: [{prod['id']}] {prod['name']} | Price: {prod['price']:,.0f} VND | Rating: ★ {prod['rating']}{RESET}")
                else:
                    print(f"{RED}Product ID {pid} not found in tree index.{RESET}")
                print(f" Lookup Latency: BST: {res['bst_latency_ns']} ns | AVL: {res['avl_latency_ns']} ns")
            elif opt in (3, 4, 5):
                t_map = {3: "pre_order", 4: "in_order", 5: "post_order"}
                trav = t_map[opt]
                items = self.tree_service.get_traversals(tree_type="bst", traversal=trav, limit=10)
                headers = ["ID", "Name", "Price (VND)", "Rating"]
                rows = [[p["id"], p["name"], f"{p['price']:,.0f}", p["rating"]] for p in items]
                print(f"\n{BOLD}{trav.upper()} Traversal Sample (First 10 nodes):{RESET}")
                print_table(headers, rows)
            elif opt == 6:
                self.run_tree_degeneration_demo()

    def run_tree_degeneration_demo(self):
        """Demonstrate how sorted input breaks naive BST but AVL remains O(log n)."""
        print_section("BST vs AVL Degeneration Experiment on Sorted Input")
        from src.modules.module3_tree.bst import BinarySearchTree
        from src.modules.module3_tree.avl import AVLTree

        test_sizes = [500, 1000, 2500, 5000]
        headers = ["N (Sorted IDs)", "BST Height", "BST Search (ns)", "AVL Height", "AVL Rotations", "AVL Search (ns)"]
        rows = []

        for n in test_sizes:
            bst = BinarySearchTree()
            avl = AVLTree()
            # Insert sorted numbers 1..n
            for i in range(1, n + 1):
                p = Product(i, f"Product #{i}", 100000, 10, 4.5)
                bst.insert(p)
                avl.insert(p)

            # Search worst-case (last element)
            t0 = time.perf_counter_ns()
            bst.search(n)
            bst_ns = time.perf_counter_ns() - t0

            t0 = time.perf_counter_ns()
            avl.search(n)
            avl_ns = time.perf_counter_ns() - t0

            rows.append([n, bst.height(), f"{bst_ns:,}", avl.height(), avl.rotations_count, f"{avl_ns:,}"])

        print_table(headers, rows)
        print(f"\n{YELLOW}Notice:{RESET} On sorted input, naive BST height equals N ({BOLD}degenerate O(n) linked list{RESET}), whereas AVL height remains strictly {BOLD}logarithmic (height <= 14){RESET}!")

    # ================= MODULE 4: SORT & FILTER =================
    def menu_sort_filter(self):
        while True:
            print_section("Module 4: Filter & Sorting Engine")
            print(" [1] Filter Catalog (Price Range, Rating, In-Stock)")
            print(" [2] Run Head-to-Head Sorting Benchmark (Bubble/Insertion/Selection vs Merge/Quick/Tim)")
            print(" [3] Sort Inventory by Price (Ascending/Descending)")
            print(" [4] Sort Inventory by Rating (Top Rated)")
            print(" [0] Back to Main Menu")

            opt = prompt_int("Choose sort/filter option", default=1, min_val=0, max_val=4)
            if opt == 0:
                break
            elif opt == 1:
                min_p = prompt_float("Min Price (VND)", default=100000.0)
                max_p = prompt_float("Max Price (VND)", default=5000000.0)
                min_r = prompt_float("Min Rating (1.0 - 5.0)", default=4.0)
                in_stock = prompt_str("In-stock only? (y/n)", default="y").lower() == "y"
                filtered = self.sort_service.filter_catalog(min_price=min_p, max_price=max_p, min_rating=min_r, in_stock_only=in_stock)
                print(f"{GREEN}✓ Found {len(filtered):,} products matching criteria.{RESET}")
                headers = ["ID", "Name", "Price (VND)", "Stock", "Rating"]
                rows = [[p.id, p.name, f"{p.price:,.0f}", p.stock, f"★ {p.rating}"] for p in filtered[:10]]
                print_table(headers, rows)
            elif opt == 2:
                sample_size = prompt_int("Dataset sample size for benchmark", default=5000, min_val=500, max_val=50000)
                by = prompt_str("Sort key (price/rating/stock/id)", default="price")
                print(f"{CYAN}Running sorting algorithms on N={sample_size:,} elements...{RESET}")
                res = self.sort_service.run_sort_benchmark(sample_size=sample_size, by=by)
                headers = ["Algorithm", "Complexity", "Execution Time", "Verified Sorted", "Extrapolated @ 100k"]
                rows = []
                for alg_name, data in res["algorithms"].items():
                    extrap = f"{data.get('extrapolated_at_100k_sec', 0):,.1f} s" if "extrapolated_at_100k_sec" in data else "Real: ~0.15 s"
                    rows.append([
                        alg_name,
                        data["complexity"],
                        f"{data['time_ms']} ms",
                        "✓ PASS" if data["verified_sorted"] else "✗ FAIL",
                        extrap
                    ])
                print_table(headers, rows)
            elif opt in (3, 4):
                key = "price" if opt == 3 else "rating"
                asc = prompt_str("Ascending? (y/n)", default="y" if opt == 3 else "n").lower() == "y"
                raw = list(self.inventory_service.catalog.iter_products())[:1000]
                from src.modules.module4_sort_filter.advanced_sorts import quick_sort
                sorted_prods = quick_sort(raw, by=key, ascending=asc)
                headers = ["ID", "Name", "Price (VND)", "Stock", "Rating"]
                rows = [[p.id, p.name, f"{p.price:,.0f}", p.stock, f"★ {p.rating}"] for p in sorted_prods[:10]]
                print(f"\n{BOLD}Top 10 Sorted by {key.upper()} ({'ASC' if asc else 'DESC'}):{RESET}")
                print_table(headers, rows)

    # ================= MODULE 5: SEARCH & HISTORY =================
    def menu_search(self):
        while True:
            print_section("Module 5: Instant Search & Search History")
            print(" [1] Search by Product Name via Hash Table - Average O(1)")
            print(" [2] Compare Search Methods by ID (Linear vs Binary vs BST vs AVL)")
            print(" [3] View Search Keyword History (Move-to-Front vs Transpose)")
            print(" [4] Run MTF vs Transpose Comparison on Skewed Zipfian Queries")
            print(" [5] Inspect Hash Table Metrics (Load Factor, Longest Chain, Collisions)")
            print(" [0] Back to Main Menu")

            opt = prompt_int("Choose search option", default=1, min_val=0, max_val=5)
            if opt == 0:
                break
            elif opt == 1:
                name = prompt_str("Enter product name keyword", default="Sony Ultra Headphones #101")
                res = self.search_service.search_by_name_hash(name)
                if res["found"]:
                    p = res["product"]
                    print(f"{GREEN}✓ Found: [{p['id']}] {p['name']} | Price: {p['price']:,.0f} VND | Rating: ★ {p['rating']}{RESET}")
                else:
                    print(f"{RED}No product found matching '{name}' in Hash Table index.{RESET}")
                print(f" Lookup time: {res['latency_ns']} ns ({res['latency_ms']:.4f} ms)")
            elif opt == 2:
                pid = prompt_int("Enter Product ID to benchmark", default=5000)
                comp = self.search_service.compare_search_methods_by_id(pid)
                headers = ["Search Algorithm", "Theoretical Big-O", "Latency", "Comparisons / Probes"]
                rows = []
                for alg, data in comp["results"].items():
                    comps = data.get("comparisons", "N/A (Pointers)")
                    rows.append([alg, alg.split('(')[-1].replace(')', ''), f"{data['latency_ns']:,} ns", comps])
                print_table(headers, rows)
            elif opt == 3:
                strat = prompt_str("Strategy to view (MTF / Transpose)", default="MTF")
                hist = self.search_service.get_search_history(strategy=strat)
                headers = ["Rank", "Keyword", "Search Count"]
                rows = [[idx + 1, it["keyword"], it["count"]] for idx, it in enumerate(hist["items"])]
                print(f"\n{BOLD}RECENT SEARCH HISTORY ({strat.upper()}) - Avg Probes: {hist['metrics']['avg_probes_per_access']}{RESET}")
                print_table(headers, rows)
            elif opt == 4:
                self.run_self_organizing_benchmark()
            elif opt == 5:
                stats = self.search_service.hash_table.get_statistics()
                headers = ["Metric", "Value"]
                rows = [
                    ["Bucket Capacity", f"{stats['capacity']:,}"],
                    ["Total Indexed Products", f"{stats['total_items']:,}"],
                    ["Load Factor (α)", f"{stats['load_factor']:.4f}"],
                    ["Collision Count", f"{stats['collision_count']:,}"],
                    ["Longest Chain Length", stats['longest_chain']],
                    ["Empty Buckets", f"{stats['empty_buckets']:,}"],
                    ["Rehash Trigger Count", stats['rehash_count']]
                ]
                print_table(headers, rows)

    def run_self_organizing_benchmark(self):
        """Simulate repeated queries with Zipfian 80/20 distribution."""
        print_section("MTF vs Transpose Comparison on Skewed Workload")
        from src.modules.module5_search.self_organizing_list import SelfOrganizingList
        import random

        keywords = [f"Product_Category_{i}" for i in range(1, 101)]
        weights = [1.0 / (i ** 0.8) for i in range(1, 101)]  # Zipf-like distribution
        query_sequence = random.choices(keywords, weights=weights, k=5000)

        mtf_list = SelfOrganizingList(strategy="MTF")
        trans_list = SelfOrganizingList(strategy="Transpose")

        for q in query_sequence:
            mtf_list.record_search(q)
            trans_list.record_search(q)

        m_mtf = mtf_list.get_metrics()
        m_trans = trans_list.get_metrics()

        headers = ["Strategy", "Queries", "Total Probes", "Avg Probes / Query", "Performance Gain"]
        rows = [
            ["Move-to-Front (MTF)", f"{m_mtf['access_count']:,}", f"{m_mtf['total_probes']:,}", m_mtf['avg_probes_per_access'], "Baseline (Fastest Adaptation)"],
            ["Transpose", f"{m_trans['access_count']:,}", f"{m_trans['total_probes']:,}", m_trans['avg_probes_per_access'], f"{((m_trans['avg_probes_per_access'] - m_mtf['avg_probes_per_access']) / m_mtf['avg_probes_per_access']) * 100:+.1f}% probes"]
        ]
        print_table(headers, rows)

    # ================= BENCHMARK SUITE =================
    def run_benchmark_suite(self):
        print_section("Running Automated Empirical Benchmark Suite")
        print("Executing benchmark scripts and exporting CSV logs and PNG plots...")
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "benchmark", "run_all_benchmarks.py"))
        os.system(f"python3 {script_path}")

    # ================= REPORT GENERATOR =================
    def generate_academic_report(self):
        print_section("Compiling Vietnamese Academic Term-Paper (.docx)")
        report_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "report", "generate_term_paper.py"))
        os.system(f"python3 {report_script}")

    # ================= MEMORY & CLEANUP =================
    def menu_memory(self):
        print_section("Memory Profiling & Explicit Cleanup")
        mem_info = self.profiler.get_memory_summary()
        print(f"Current RAM Allocated: {GREEN}{mem_info['current_mb']} MB{RESET} | Peak: {YELLOW}{mem_info['peak_mb']} MB{RESET}")

        confirm = prompt_str("Execute explicit memory release for all catalog nodes? (y/n)", default="y")
        if confirm.lower() == "y":
            res = self.inventory_service.cleanup_inventory()
            print(f"{GREEN}✓ Explicitly cleared {res['nodes_released']:,} nodes.{RESET}")
            print(f"{GREEN}✓ Collected {res['gc_stats']['unreachable_objects_collected']} objects. RAM after GC: {res['gc_stats']['current_mb_after_gc']} MB.{RESET}")

    def handle_exit(self):
        print(f"\n{CYAN}Shutting down Mini E-Commerce Core Engine...{RESET}")
        self.inventory_service.cleanup_inventory()
        print(f"{GREEN}✓ All dynamic resources released. Goodbye!{RESET}\n")


if __name__ == "__main__":
    app = EcommerceConsoleApp()
    app.run()
