# Mini E-Commerce Core Engine (DSA Term Project)

A high-performance Python console e-commerce core engine managing 100,000+ Product objects across 5 custom DSA business modules, backed by real empirical benchmarks, memory profiling, and a complete Vietnamese academic term paper (.docx).

## User Review & Critical Decisions

> [!IMPORTANT]
> Key architectural decisions proposed for approval:
> 1. **Doubly Linked List for Inventory**: We choose a Doubly Linked List with `head` and `tail` pointers to ensure true $O(1)$ operations at both ends (`add_head`, `add_tail`) and clean $O(1)$ node removal once a node is located, while avoiding Python's built-in `list` (static dynamic array).
> 2. **Recursion Limit & Balanced Tree**: Python's default recursion limit (1000) causes stack overflow on degenerated BSTs with 100,000 sorted elements. We will configure `sys.setrecursionlimit(250000)` for deep traversals and utilize an AVL self-balancing tree to guarantee $O(\log n)$ height ($h \le 1.44 \log_2 n \approx 24$ levels for $n=100,000$).
> 3. **Python $O(n^2)$ Sorting Scale**: Pure Python quadratic algorithms (Selection/Bubble/Insertion Sort) on 100,000 elements perform $\approx 10^{10}$ comparisons, taking hours. We implement a stratified benchmark: $O(n^2)$ sorts are tested on $N \in [500, 1000, 2000, 5000, 10000]$ with polynomial regression extrapolation to $N=100,000$, while $O(n \log n)$ algorithms (QuickSort, MergeSort) and CPython TimSort are benchmarked up to the full $100,000+$ items.
> 4. **Deliverable Format**: A clean terminal console interface with robust menu navigation, paired with Python-docx generation producing the 7-chapter Vietnamese report with embedded benchmark charts and tables.

---

## 1. Overview & Core Concept
- **Domain**: High-scale E-Commerce core engine demonstrating foundational Data Structures & Algorithms without relying on black-box container libraries.
- **Data Scale**: $\ge 100,000$ products with attributes `ID` (integer / formatted string), `Name` (str), `Price` (float), `Stock` (int), `Rating` (float $\in [1.0, 5.0]$).
- **Core Modules**:
  1. *Catalog & Inventory*: Doubly Linked List, CSV bulk loader, pagination, explicit node teardown.
  2. *Cart & Order Processing*: Stack (LIFO cart undo) and Queue (FIFO flash-sale order queue with stock decrement & logs).
  3. *High-speed Index*: BST & AVL tree keyed by Product ID with recursive traversals (Pre/In/Post).
  4. *Filter & Sorting Engine*: Price/Rating filters, Selection & Insertion sort ($O(n^2)$), MergeSort & QuickSort ($O(n \log n)$), visual CLI comparison table.
  5. *Instant Search & History*: Hash table (Separate Chaining, string hashing, load factor, dynamic rehashing), Self-organizing list (Move-to-Front vs. Transpose), Linear vs. Binary search.
  6. *Benchmarks & Term Paper*: Automated test suites (`pytest`), CSV/PNG benchmark exports, and a 7-chapter `.docx` term paper in academic Vietnamese.

---

## 2. User Experience & Console Architecture

### Console UI Flow
```
┌─────────────────────────────────────────────────────────────┐
│             MINI E-COMMERCE CORE ENGINE (DSA)               │
│               Dataset: 100,000 Products Loaded              │
├─────────────────────────────────────────────────────────────┤
│ [1] Catalog & Inventory (Doubly Linked List)                │
│     - Browse (Paginated 20/page), Add Head/Tail, Delete ID  │
│ [2] Cart & Flash Sale Checkout                              │
│     - Add to Cart, Remove & Undo (Stack), Flash Sale (Queue)│
│ [3] High-Speed ID Index (BST & AVL Trees)                   │
│     - Lookup, Insert, Delete, Traversals (Pre/In/Post)      │
│ [4] Filter & Sorting Engine                                 │
│     - Filter Range, Sort (Bubble/Select/Merge/Quick), Stats │
│ [5] Search Engine & Keyword History                         │
│     - Hash Table Lookup, MTF vs Transpose Recent Searches   │
│ [6] Run Full Benchmark Suite (CSV & PNG Export)             │
│ [7] Generate Academic Report (.docx)                        │
│ [8] Memory Profile & Cleanup (Explicit Pointer Teardown)    │
│ [0] Exit Application                                        │
└─────────────────────────────────────────────────────────────┘
```

- **Defensive CLI**: Every input is wrapped in try-catch with graceful parsing; out-of-range choices, invalid types, and empty inputs never cause program termination.
- **ANSI Terminal Styling**: Clean borders, colored status tags (`[SUCCESS]`, `[WARNING]`, `[INFO]`), and clear table formatting.

---

## 3. Key Product Decisions & Trade-Offs

### 3.1 Linked List Choice: Doubly Linked List with Sentinel
- **Decision**: Doubly Linked List with `head` and `tail` pointers.
- **Why**: Allows true $O(1)$ insertion at head and tail without scanning $N$ items. Enables efficient backward iteration and localized $O(1)$ node removal once pointer is located.
- **Alternative**: Singly linked list requires $O(n)$ traversal to delete the tail node.

### 3.2 Tree Degeneration Mitigation: AVL Balancing
- **Decision**: Implement both pure BST and AVL Tree (with Left, Right, Left-Right, Right-Left rotations).
- **Why**: Sorted product ID inputs turn a naive BST into a linked list with $O(n)$ search depth and stack overflow risk. AVL strictly enforces $|h_L - h_R| \le 1$, guaranteeing $O(\log n)$ search under all insertion patterns.

### 3.3 Hash Table Design: Polynomial Rolling Hash & Separate Chaining
- **Decision**: Polynomial rolling hash function $H(s) = (\sum_{i=0}^{m-1} s[i] \cdot p^i) \pmod M$ ($p=31, M=\text{prime}$) with bucket arrays holding singly linked lists.
- **Why**: Handles arbitrary product name strings evenly across buckets. Separate chaining provides robust collision handling with simple pointer chaining and clean rehash triggers when load factor $\alpha = \frac{n}{M} > 0.75$.

### 3.4 Self-Organizing Search History: Move-to-Front (MTF) vs. Transpose
- **Decision**: Implement both heuristics on a linked list. MTF moves accessed keyword immediately to head ($O(1)$ after find); Transpose swaps the keyword with its immediate predecessor.
- **Why**: Enables empirical comparison demonstrating 80/20 Zipfian access patterns where MTF adapts faster to sudden bursts while Transpose prevents outlier queries from evicting hot items.

---

## 4. Technical Architecture & System Flow

```
+-------------------------------------------------------------------------+
|                               MAIN MENU                                 |
|                               (main.py)                                 |
+----+---------------+---------------+---------------+---------------+----+
     |               |               |               |               |
     v               v               v               v               v
+----------+   +----------+    +----------+    +----------+    +----------+
| Module 1 |   | Module 2 |    | Module 3 |    | Module 4 |    | Module 5 |
| Catalog  |   | Cart &   |    | ID Index |    | Filter & |    | Search & |
| Inventory|   | Checkout |    | BST/AVL  |    | Sorting  |    | History  |
+----+-----+   +----+-----+    +----+-----+    +----+-----+    +----+-----+
     |              |               |               |               |
     | [Doubly LL]  | [Stack/Queue] | [BST & AVL]   | [Merge/Quick] | [Hash/MTF]
     +--------------+---------------+---------------+---------------+
                                    |
                                    v
                     +-----------------------------+
                     |    Core ADT: Product        |
                     |  (ID, Name, Price, Stock,   |
                     |   Rating, Slots/Memory)     |
                     +--------------+--------------+
                                    |
            +-----------------------+-----------------------+
            v                                               v
+-----------------------+                       +-----------------------+
|   Benchmark Engine    |                       | Report Builder (.docx)|
| - Sort Scenarios      |                       | - 7 Vietnamese Chaps  |
| - Search Latencies    |                       | - Embedded Charts     |
| - Memory Profiling    |                       | - Complexity Tables   |
+-----------------------+                       +-----------------------+
```

---

## 5. Verification & Testing Strategy
- **Unit Tests (`pytest tests/`)**:
  - `test_catalog.py`: DLL add_head, add_tail, delete_id, pagination, node count, cleanup.
  - `test_cart_order.py`: Stack push/pop/undo, Queue enqueue/dequeue, FIFO order, stock validation.
  - `test_tree_index.py`: BST insert/search/delete, AVL balance invariant, traversals.
  - `test_sorting.py`: Selection, Insertion, MergeSort, QuickSort correctness against edge cases (empty, single, sorted, reverse, duplicates).
  - `test_search.py`: Linear, Binary, Hash Table (collisions, rehashing), MTF and Transpose list reordering.
- **Benchmark Suite**: Script producing CSV datasets in `/benchmark/results/` and matplotlib/seaborn plots in `/benchmark/plots/`.
- **Term Paper Generation**: Automated Python script utilizing `python-docx` to produce the complete academic paper conforming to university thesis standards.
