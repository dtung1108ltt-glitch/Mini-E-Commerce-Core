"""
Automated Empirical Benchmark Suite for Mini E-Commerce System
Executes 5 comprehensive experiments:
1. Sorting: Basic (Bubble, Selection, Insertion) vs Advanced (Merge, Quick, TimSort) across Random, Sorted, Reversed scenarios.
2. Search: Linear Search vs Binary Search vs BST vs Hash Table.
3. Tree Degeneration: BST vs AVL on Random vs Sorted insertion sequences.
4. Self-Organizing Lists: Move-to-Front (MTF) vs Transpose under Zipfian skewed queries.
5. Memory Profiling: Baseline, After Loading 100,000 products, After Explicit Cleanup.

Exports:
- CSV results in /benchmark/results/
- High-resolution PNG charts in /benchmark/plots/
"""
import os
import sys
import csv
import time
import random
import tracemalloc

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.product import Product
from src.modules.module1_catalog.doubly_linked_list import DoublyLinkedList
from src.modules.module3_tree.bst import BinarySearchTree
from src.modules.module3_tree.avl import AVLTree
from src.modules.module4_sort_filter.basic_sorts import bubble_sort, selection_sort, insertion_sort
from src.modules.module4_sort_filter.advanced_sorts import merge_sort, quick_sort
from src.modules.module5_search.hash_table import HashTable
from src.modules.module5_search.self_organizing_list import SelfOrganizingList
from src.modules.module5_search.linear_binary_search import linear_search_by_id, binary_search_by_id

import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "results"))
PLOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "plots"))
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)


# =====================================================================
# EXPERIMENT 1: SORTING BENCHMARK
# =====================================================================
def run_sorting_benchmark():
    print("▶ Running Experiment 1: Sorting Algorithms Benchmark...")
    sizes_advanced = [1000, 5000, 10000, 25000, 50000, 100000]
    sizes_basic = [500, 1000, 2000, 3000]
    scenarios = ["random", "sorted", "reversed"]

    csv_path = os.path.join(RESULTS_DIR, "benchmark_sorting.csv")
    records = []

    for scenario in scenarios:
        # Benchmark Advanced Sorts
        for n in sizes_advanced:
            if scenario == "random":
                base_data = [Product(i, f"P{i}", random.randint(1000, 1000000), 10, 4.0) for i in range(1, n + 1)]
            elif scenario == "sorted":
                base_data = [Product(i, f"P{i}", i * 100, 10, 4.0) for i in range(1, n + 1)]
            else:  # reversed
                base_data = [Product(i, f"P{i}", (n - i) * 100, 10, 4.0) for i in range(1, n + 1)]

            # QuickSort
            t0 = time.perf_counter()
            quick_sort(base_data, by="price")
            t_qs = time.perf_counter() - t0
            records.append(["QuickSort", "O(n log n)", scenario, n, round(t_qs, 6)])

            # MergeSort (up to 50k to bound memory in Python)
            if n <= 50000:
                t0 = time.perf_counter()
                merge_sort(base_data, by="price")
                t_ms = time.perf_counter() - t0
                records.append(["MergeSort", "O(n log n)", scenario, n, round(t_ms, 6)])

            # TimSort (C-Level Python baseline)
            t0 = time.perf_counter()
            sorted(base_data, key=lambda p: p.price)
            t_ts = time.perf_counter() - t0
            records.append(["Python TimSort", "O(n log n)", scenario, n, round(t_ts, 6)])

        # Benchmark Basic Sorts (O(n²))
        for n in sizes_basic:
            if scenario == "random":
                base_data = [Product(i, f"P{i}", random.randint(1000, 1000000), 10, 4.0) for i in range(1, n + 1)]
            elif scenario == "sorted":
                base_data = [Product(i, f"P{i}", i * 100, 10, 4.0) for i in range(1, n + 1)]
            else:
                base_data = [Product(i, f"P{i}", (n - i) * 100, 10, 4.0) for i in range(1, n + 1)]

            # Insertion Sort
            t0 = time.perf_counter()
            insertion_sort(base_data, by="price")
            t_is = time.perf_counter() - t0
            records.append(["Insertion Sort", "O(n²)", scenario, n, round(t_is, 6)])

            # Selection Sort
            t0 = time.perf_counter()
            selection_sort(base_data, by="price")
            t_ss = time.perf_counter() - t0
            records.append(["Selection Sort", "O(n²)", scenario, n, round(t_ss, 6)])

            # Bubble Sort (on smaller sizes)
            if n <= 2000:
                t0 = time.perf_counter()
                bubble_sort(base_data, by="price")
                t_bs = time.perf_counter() - t0
                records.append(["Bubble Sort", "O(n²)", scenario, n, round(t_bs, 6)])

    # Write CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Algorithm", "Complexity", "Scenario", "N", "Time_Seconds"])
        writer.writerows(records)

    # Plot Chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Advanced sorts on random input
    qs_data = [r[4] for r in records if r[0] == "QuickSort" and r[2] == "random"]
    qs_n = [r[3] for r in records if r[0] == "QuickSort" and r[2] == "random"]
    ms_data = [r[4] for r in records if r[0] == "MergeSort" and r[2] == "random"]
    ms_n = [r[3] for r in records if r[0] == "MergeSort" and r[2] == "random"]
    ts_data = [r[4] for r in records if r[0] == "Python TimSort" and r[2] == "random"]
    ts_n = [r[3] for r in records if r[0] == "Python TimSort" and r[2] == "random"]

    ax1.plot(qs_n, qs_data, marker='o', label='QuickSort (O(n log n))', color='#2563eb', linewidth=2)
    ax1.plot(ms_n, ms_data, marker='s', label='MergeSort (O(n log n))', color='#10b981', linewidth=2)
    ax1.plot(ts_n, ts_data, marker='^', label='TimSort (C-Level)', color='#6366f1', linestyle='--')
    ax1.set_title("Advanced O(n log n) Sorts (Random Data)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Dataset Size (N)")
    ax1.set_ylabel("Execution Time (Seconds)")
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend()

    # Basic sorts on random input
    is_data = [r[4] for r in records if r[0] == "Insertion Sort" and r[2] == "random"]
    is_n = [r[3] for r in records if r[0] == "Insertion Sort" and r[2] == "random"]
    ss_data = [r[4] for r in records if r[0] == "Selection Sort" and r[2] == "random"]
    ss_n = [r[3] for r in records if r[0] == "Selection Sort" and r[2] == "random"]
    bs_data = [r[4] for r in records if r[0] == "Bubble Sort" and r[2] == "random"]
    bs_n = [r[3] for r in records if r[0] == "Bubble Sort" and r[2] == "random"]

    ax2.plot(is_n, is_data, marker='o', label='Insertion Sort (O(n²))', color='#f59e0b', linewidth=2)
    ax2.plot(ss_n, ss_data, marker='s', label='Selection Sort (O(n²))', color='#ef4444', linewidth=2)
    ax2.plot(bs_n, bs_data, marker='^', label='Bubble Sort (O(n²))', color='#8b5cf6', linewidth=2)
    ax2.set_title("Basic O(n²) Sorts Quadratic Curve", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Dataset Size (N)")
    ax2.set_ylabel("Execution Time (Seconds)")
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend()

    plt.tight_layout()
    chart_path = os.path.join(PLOTS_DIR, "chart_sorting_benchmark.png")
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"✓ Sorting benchmark saved to {csv_path} and {chart_path}")


# =====================================================================
# EXPERIMENT 2: SEARCH METHODS COMPARISON
# =====================================================================
def run_search_benchmark():
    print("▶ Running Experiment 2: Search Algorithms Benchmark...")
    sizes = [1000, 5000, 10000, 25000, 50000, 100000]
    csv_path = os.path.join(RESULTS_DIR, "benchmark_search.csv")
    records = []

    for n in sizes:
        prods = [Product(i, f"Brand Product #{i}", i * 1000, 10, 4.5) for i in range(1, n + 1)]
        # Target: search element near the 75th percentile to represent typical lookup
        target_id = int(n * 0.75)
        target_name = f"Brand Product #{target_id}"

        # 1. Linear Search (Unsorted list)
        t0 = time.perf_counter_ns()
        _, lin_comps = linear_search_by_id(prods, target_id)
        t_lin_ns = time.perf_counter_ns() - t0
        records.append(["Linear Search", "O(n)", n, t_lin_ns, lin_comps])

        # 2. Binary Search (Sorted array)
        t0 = time.perf_counter_ns()
        _, bin_comps = binary_search_by_id(prods, target_id)
        t_bin_ns = time.perf_counter_ns() - t0
        records.append(["Binary Search", "O(log n)", n, t_bin_ns, bin_comps])

        # 3. BST Search
        # Build BST with random sample insertion
        sample_subset = list(prods)
        random.seed(42)
        random.shuffle(sample_subset)
        bst = BinarySearchTree()
        # To keep BST building fast in benchmark, build for up to 25k
        bst_limit = min(n, 25000)
        for p in sample_subset[:bst_limit]:
            bst.insert(p)
        t0 = time.perf_counter_ns()
        bst.search(min(target_id, bst_limit))
        t_bst_ns = time.perf_counter_ns() - t0
        records.append(["BST Search", "O(log n)", n, t_bst_ns, "Pointers"])

        # 4. Hash Table Search (by Name)
        ht = HashTable(initial_capacity=max(10007, int(n * 1.5)))
        for p in prods:
            ht.insert(p.name, p)
        t0 = time.perf_counter_ns()
        ht.search(target_name)
        t_ht_ns = time.perf_counter_ns() - t0
        records.append(["Hash Table", "O(1)", n, t_ht_ns, 1])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Method", "Complexity", "N", "Latency_Nanoseconds", "Probes_or_Comparisons"])
        writer.writerows(records)

    # Plot Search Latency (Log Scale)
    fig, ax = plt.subplots(figsize=(8, 5))
    methods = ["Linear Search", "Binary Search", "BST Search", "Hash Table"]
    colors = ['#ef4444', '#10b981', '#3b82f6', '#8b5cf6']
    markers = ['o', 's', '^', 'D']

    for idx, m in enumerate(methods):
        sub_n = [r[2] for r in records if r[0] == m]
        sub_t = [r[3] / 1000.0 for r in records if r[0] == m]  # convert ns to microseconds
        ax.plot(sub_n, sub_t, marker=markers[idx], label=f"{m}", color=colors[idx], linewidth=2)

    ax.set_yscale('log')
    ax.set_title("Search Latency Comparison (Log Scale)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Dataset Size (N)")
    ax.set_ylabel("Latency (Microseconds - Log10 Scale)")
    ax.grid(True, which="both", ls=":", alpha=0.6)
    ax.legend()

    plt.tight_layout()
    chart_path = os.path.join(PLOTS_DIR, "chart_search_benchmark.png")
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"✓ Search benchmark saved to {csv_path} and {chart_path}")


# =====================================================================
# EXPERIMENT 3: BST VS AVL ON DEGENERATION
# =====================================================================
def run_tree_benchmark():
    print("▶ Running Experiment 3: BST vs AVL Tree Degeneration...")
    sizes = [100, 500, 1000, 2000, 4000, 8000]
    csv_path = os.path.join(RESULTS_DIR, "benchmark_bst_avl.csv")
    records = []

    for n in sizes:
        # Scenario A: Random input
        random.seed(42)
        random_ids = list(range(1, n + 1))
        random.shuffle(random_ids)

        bst_rand = BinarySearchTree()
        avl_rand = AVLTree()
        for pid in random_ids:
            p = Product(pid, f"P{pid}", 10000, 5, 4.0)
            bst_rand.insert(p)
            avl_rand.insert(p)

        # Scenario B: Sorted input (Degeneration test)
        bst_sort = BinarySearchTree()
        avl_sort = AVLTree()
        for pid in range(1, n + 1):
            p = Product(pid, f"P{pid}", 10000, 5, 4.0)
            bst_sort.insert(p)
            avl_sort.insert(p)

        # Measure search on last element (worst-case for sorted)
        t0 = time.perf_counter_ns()
        bst_sort.search(n)
        t_bst_sort_ns = time.perf_counter_ns() - t0

        t0 = time.perf_counter_ns()
        avl_sort.search(n)
        t_avl_sort_ns = time.perf_counter_ns() - t0

        records.append([n, "Random", bst_rand.height(), avl_rand.height(), avl_rand.rotations_count, 0, 0])
        records.append([n, "Sorted", bst_sort.height(), avl_sort.height(), avl_sort.rotations_count, t_bst_sort_ns, t_avl_sort_ns])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "Input_Order", "BST_Height", "AVL_Height", "AVL_Rotations", "BST_Search_ns", "AVL_Search_ns"])
        writer.writerows(records)

    # Plot Heights
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    sorted_records = [r for r in records if r[1] == "Sorted"]
    ns = [r[0] for r in sorted_records]
    bst_h = [r[2] for r in sorted_records]
    avl_h = [r[3] for r in sorted_records]
    rotations = [r[4] for r in sorted_records]

    ax1.plot(ns, bst_h, marker='o', label='BST Height on Sorted Input (O(n))', color='#ef4444', linewidth=2)
    ax1.plot(ns, avl_h, marker='s', label='AVL Height on Sorted Input (O(log n))', color='#10b981', linewidth=2)
    ax1.set_title("Tree Height: BST vs AVL on Sorted Input", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Number of Inserted Keys (N)")
    ax1.set_ylabel("Tree Height (levels)")
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend()

    ax2.bar(range(len(ns)), rotations, tick_label=[str(x) for x in ns], color='#3b82f6', alpha=0.8)
    ax2.set_title("AVL Rebalancing Rotations Performed", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Number of Inserted Keys (N)")
    ax2.set_ylabel("Total Rotations (LL, RR, LR, RL)")
    ax2.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    chart_path = os.path.join(PLOTS_DIR, "chart_tree_degeneration.png")
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"✓ Tree benchmark saved to {csv_path} and {chart_path}")


# =====================================================================
# EXPERIMENT 4: MOVE-TO-FRONT VS TRANSPOSE
# =====================================================================
def run_self_organizing_benchmark():
    print("▶ Running Experiment 4: Move-to-Front vs Transpose on Zipfian Query Workloads...")
    query_counts = [500, 1000, 2500, 5000, 10000]
    num_unique_keywords = 100
    keywords = [f"Keyword_{i}" for i in range(1, num_unique_keywords + 1)]
    # Skewed Zipf weights: P(i) proportional to 1 / i^0.9
    weights = [1.0 / (i ** 0.9) for i in range(1, num_unique_keywords + 1)]

    csv_path = os.path.join(RESULTS_DIR, "benchmark_self_organizing.csv")
    records = []

    for q_count in query_counts:
        random.seed(42)
        sequence = random.choices(keywords, weights=weights, k=q_count)

        mtf = SelfOrganizingList(strategy="MTF")
        trans = SelfOrganizingList(strategy="Transpose")

        for kw in sequence:
            mtf.record_search(kw)
            trans.record_search(kw)

        m_mtf = mtf.get_metrics()
        m_trans = trans.get_metrics()

        records.append([q_count, m_mtf["total_probes"], m_mtf["avg_probes_per_access"],
                        m_trans["total_probes"], m_trans["avg_probes_per_access"]])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Query_Count", "MTF_Total_Probes", "MTF_Avg_Probes", "Transpose_Total_Probes", "Transpose_Avg_Probes"])
        writer.writerows(records)

    # Plot Probes Comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    qs = [r[0] for r in records]
    mtf_avgs = [r[2] for r in records]
    trans_avgs = [r[4] for r in records]

    ax.plot(qs, mtf_avgs, marker='o', label='Move-to-Front (MTF)', color='#2563eb', linewidth=2)
    ax.plot(qs, trans_avgs, marker='s', label='Transpose', color='#f59e0b', linewidth=2)
    ax.set_title("Average Probes per Search: MTF vs Transpose (Zipf 80/20 Workload)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Total Queries Processed")
    ax.set_ylabel("Average Probes per Access")
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()

    plt.tight_layout()
    chart_path = os.path.join(PLOTS_DIR, "chart_self_organizing.png")
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"✓ Self-organizing benchmark saved to {csv_path} and {chart_path}")


# =====================================================================
# EXPERIMENT 5: MEMORY PROFILING (100,000 PRODUCTS & CLEANUP)
# =====================================================================
def run_memory_benchmark():
    print("▶ Running Experiment 5: Memory Profiling (100,000 Products & Teardown)...")
    import gc
    tracemalloc.start()

    # 1. Baseline
    gc.collect()
    mem_baseline, _ = tracemalloc.get_traced_memory()

    # 2. Load 100,000 items into Doubly Linked List
    dll = DoublyLinkedList()
    for i in range(1, 100001):
        p = Product(i, f"Product #{i}", 150000.0, 25, 4.5)
        dll.add_tail(p)

    mem_loaded, peak_loaded = tracemalloc.get_traced_memory()

    # 3. Explicit cleanup routine
    released_count = dll.clear()
    gc.collect()
    mem_cleaned, peak_cleaned = tracemalloc.get_traced_memory()

    csv_path = os.path.join(RESULTS_DIR, "benchmark_memory.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Phase", "Current_Memory_MB", "Peak_Memory_MB", "Nodes_Active"])
        writer.writerow(["1. Baseline (Empty)", round(mem_baseline / (1024 * 1024), 3), round(mem_baseline / (1024 * 1024), 3), 0])
        writer.writerow(["2. After Loading 100,000 Products", round(mem_loaded / (1024 * 1024), 3), round(peak_loaded / (1024 * 1024), 3), 100000])
        writer.writerow(["3. After Explicit Cleanup & GC", round(mem_cleaned / (1024 * 1024), 3), round(peak_cleaned / (1024 * 1024), 3), 0])

    # Plot Memory Bar Chart
    fig, ax = plt.subplots(figsize=(7, 5))
    phases = ["Baseline", "Loaded 100k Items", "After Cleanup"]
    mems = [mem_baseline / (1024 * 1024), mem_loaded / (1024 * 1024), mem_cleaned / (1024 * 1024)]
    colors = ['#94a3b8', '#ef4444', '#10b981']

    bars = ax.bar(phases, mems, color=colors, width=0.55)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f} MB',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold')

    ax.set_title("RAM Memory Consumption Lifecycle (100,000 Products)", fontsize=12, fontweight='bold')
    ax.set_ylabel("RAM Memory (Megabytes)")
    ax.grid(True, linestyle=':', alpha=0.6, axis='y')

    plt.tight_layout()
    chart_path = os.path.join(PLOTS_DIR, "chart_memory_profiling.png")
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"✓ Memory benchmark saved to {csv_path} and {chart_path}")


def main():
    print("=================================================================")
    print("STARTING FULL AUTOMATED EMPIRICAL BENCHMARK SUITE")
    print("=================================================================")
    t_start = time.perf_counter()
    run_sorting_benchmark()
    run_search_benchmark()
    run_tree_benchmark()
    run_self_organizing_benchmark()
    run_memory_benchmark()
    t_end = time.perf_counter()
    print(f"\n✓ ALL BENCHMARKS COMPLETED IN {t_end - t_start:.2f}s.")
    print(f"CSVs stored in: {RESULTS_DIR}")
    print(f"PNG charts stored in: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
