# Mini E-Commerce Core Engine (DSA Term Project)

A high-performance Python console & web application managing **100,000+ Product objects** using custom fundamental Data Structures and Algorithms without static arrays or external black-box collections.

Includes 5 business modules, a comprehensive test suite (`pytest`), automated empirical benchmark engine (CSV + PNG plots), and an academic term paper (.docx) written in Vietnamese according to university thesis standards.

---

## 1. Architecture Overview (3-Tier Decoupled Design)

The system adheres strictly to the **No DSA Shortcuts** rule: all data structures, algorithms, memory cleanup routines, and timing benchmarks are implemented in pure Python. The web layer is strictly a visualizer and remote controller; it never shortcuts or replicates DSA logic.

```
       +--------------------------------------------------------------+
       |                  PRESENTATION LAYER (UI/UX)                  |
       |  React 19 + TypeScript + Tailwind CSS (Vite @ port 3000)     |
       |  - Server-Side Paginated Catalog Table (10/20/50/100 items)  |
       |  - Interactive LIFO Undo Stack & FIFO Flash Sale Visualizer  |
       |  - BST vs AVL Subtree Visualizer & Degeneration Simulator    |
       |  - Filter & Sorting Race View + Step-by-Step Sorting Player  |
       |  - Hash Bucket Occupancy Inspector & Self-Organizing History |
       |  - Academic Thesis & Defense Prep (5 Core Q&A Cards)         |
       +------------------------------+-------------------------------+
                                      | HTTP REST / JSON (Express Proxy)
                                      v
       +--------------------------------------------------------------+
       |                  BRIDGE LAYER (FastAPI API)                  |
       |  FastAPI (src/api/app.py) & Express Dev Bridge (server.ts)   |
       |  - Pure delegate controller (zero DSA logic in bridge)       |
       |  - Honest timing via time.perf_counter() inside Python core  |
       |  - Server-side pagination & bounded payload transfer         |
       +------------------------------+-------------------------------+
                                      | Direct In-Memory Calls
                                      v
       +--------------------------------------------------------------+
       |                     CORE DSA ENGINE (Python)                 |
       |  Module 1: DoublyLinkedList with __slots__ & explicit clear  |
       |  Module 2: LinkedStack (LIFO Undo) & LinkedQueue (FIFO Sale) |
       |  Module 3: BST & AVL Tree with 4 Rotations (LL, RR, LR, RL)  |
       |  Module 4: Bubble/Selection/Insertion vs Merge/QuickSort     |
       |  Module 5: Hash Table (Separate Chaining) & MTF / Transpose  |
       +--------------------------------------------------------------+
```

---

## 2. Directory Structure

```
├── data/
│   ├── generate_mock_data.py          # Synthetic generator for 100,000+ realistic products
│   └── products_100k.csv              # Generated dataset (100k items)
├── src/
│   ├── main.py                        # Console menu application (Defensive CLI)
│   ├── api/
│   │   └── app.py                     # Thin FastAPI bridge (pure delegation)
│   ├── core/
│   │   ├── product.py                 # Product ADT with __slots__ optimization
│   │   └── memory_manager.py          # Tracemalloc profiler & GC tracker
│   ├── modules/
│   │   ├── module1_catalog/           # Doubly Linked List, pagination, cleanup
│   │   ├── module2_cart/              # Stack (Undo) and Queue (Flash Sale)
│   │   ├── module3_tree/              # BST and AVL Trees with 4 rotations
│   │   ├── module4_sort_filter/       # Filters, Bubble/Select/Insert vs Merge/QuickSort
│   │   └── module5_search/            # Hash Table (Separate Chaining), MTF, Transpose
│   └── utils/
│       └── cli_formatter.py           # ANSI styling, table renderer & input sanitizers
├── ui/                                # React 19 Frontend
│   └── src/
│       ├── components/                # Modular UI components for all 5 modules + Defense
│       └── translations.ts            # Bilingual support (Vietnamese default & English)
├── tests/                             # 19 pytest unit tests (13 Core DSA + 6 FastAPI API)
├── benchmark/
│   ├── run_all_benchmarks.py          # Automated benchmark runner (CSV & PNG export)
│   ├── results/                       # Exported benchmark CSV logs (5 benchmarks)
│   └── plots/                         # High-resolution PNG graphs
├── report/
│   ├── generate_term_paper.py         # Automated term-paper docx generator (7 chapters)
│   └── BCTieuLuan_CTDL_GT_Nhom.docx   # Academic report in Vietnamese (645 KB)
├── server.ts                          # Express + Vite Full-Stack Server
├── README.md                          # Project documentation
└── TRACEABILITY.md                    # Requirements-to-code traceability matrix
```

---

## 3. Installation & Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Install Dependencies
```bash
# Python dependencies
pip install fastapi uvicorn pytest matplotlib python-docx

# Web dependencies
npm install
```

### 2. Run All Unit Tests (19/19 Passing)
```bash
pytest tests -v
```

### 3. Start the Web Dashboard (One Command)
```bash
npm run dev
```
Open your browser at `http://localhost:3000`. The server serves the React UI and proxies API calls seamlessly to the Python core backend.

### 4. Run the Standalone Console CLI Application
```bash
python3 src/main.py
```

### 5. Run Benchmarks & Generate Plots
```bash
python3 benchmark/run_all_benchmarks.py
```

### 6. Compile Vietnamese Academic Report (.docx)
```bash
python3 report/generate_term_paper.py
```
Outputs `report/BCTieuLuan_CTDL_GT_Nhom.docx` formatted to university standards with embedded plots, complexity analysis, architecture diagrams, and oral defense prep.

---

## 4. Running on Windows

To run the project on a Windows machine:
1. Open PowerShell or Command Prompt.
2. Ensure Python 3.10+ and Node.js 18+ are in your `PATH`.
3. Run:
```powershell
pip install fastapi uvicorn pytest matplotlib python-docx
npm install
npm run dev
```
Navigate to `http://localhost:3000` in Google Chrome or Microsoft Edge.

---

## 4. Big-O Complexity Summary

| Structure / Algorithm | Best Case | Average Case | Worst Case | Space Complexity |
| :--- | :---: | :---: | :---: | :---: |
| **Doubly Linked List (Head/Tail)** | $O(1)$ | $O(1)$ | $O(1)$ | $O(n)$ |
| **Doubly Linked List (Delete by ID)** | $O(1)$ | $O(n)$ | $O(n)$ | $O(1)$ |
| **Stack (LIFO Undo)** | $O(1)$ | $O(1)$ | $O(1)$ | $O(n)$ |
| **Queue (FIFO Checkout)** | $O(1)$ | $O(1)$ | $O(1)$ | $O(n)$ |
| **Binary Search Tree (BST)** | $O(\log n)$ | $O(\log n)$ | $O(n)$ *(Degenerated)* | $O(n)$ |
| **AVL Tree (Self-Balancing)** | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ *(Strict)* | $O(n)$ |
| **Hash Table (Separate Chaining)** | $O(1)$ | $O(1)$ | $O(n)$ *(All Collide)* | $O(n)$ |
| **Basic Sorts (Insertion / Selection)** | $O(n) / O(n^2)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ |
| **MergeSort (Divide & Conquer)** | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ |
| **QuickSort (Median-of-Three)** | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(\log n)$ |
