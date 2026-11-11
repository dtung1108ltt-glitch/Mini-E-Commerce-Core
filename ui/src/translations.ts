/**
 * Bilingual UI Translation Dictionary (Vietnamese default + English switch)
 */
export type Language = 'vi' | 'en';

export const translations = {
  vi: {
    appTitle: "LÕI HỆ THỐNG MINI E-COMMERCE",
    appSubtitle: "Đồ án Cấu Trúc Dữ Liệu & Giải Thuật • Quản lý 100,000+ Sản Phẩm",
    navDashboard: "Tổng Quan",
    navCatalog: "1. Kho Hàng (DLL)",
    navCart: "2. Giỏ Hàng & Flash Sale (Stack/Queue)",
    navTree: "3. Chỉ Mục Cây (BST/AVL)",
    navSort: "4. Lọc & Sắp Xếp (O(n²) vs O(n log n))",
    navSearch: "5. Tìm Kiếm & Lịch Sử (Hash/MTF)",
    navBenchmarks: "Thực Nghiệm (Biểu Đồ)",
    navMemory: "Bộ Nhớ & Dọn Dẹp",

    // System stats
    systemStatus: "Trạng thái hệ thống",
    loadedProducts: "Sản phẩm đã nạp",
    currentMemory: "Bộ nhớ hiện tại",
    peakMemory: "Bộ nhớ đỉnh",
    structuresBuilt: "Cấu trúc đã dựng",

    // Actions
    quickActions: "Thao Tác Nhanh",
    load100k: "Nạp 100,000 Sản Phẩm",
    buildIndexes: "Xây Dựng Toàn Bộ Chỉ Mục",
    runDemo: "Chạy Kịch Bản Mẫu",
    releaseMemory: "Giải Phóng Bộ Nhớ (GC)",

    // Module 1
    m1Title: "Phân Hệ 1: Quản Lý Kho Hàng Động (Danh Sách Liên Kết Đôi)",
    m1Desc: "Lưu trữ động bằng Danh sách liên kết đôi (Doubly Linked List). Thêm đầu/đuôi O(1), duyệt hai chiều, phân trang phía máy chủ và giải phóng bộ nhớ tường minh.",
    m1Explain: "Nguyên lý hoạt động: Danh sách liên kết đôi sử dụng các con trỏ prev và next để liên kết các nút sản phẩm, cho phép thêm phần tử ở đầu (add_head) hoặc cuối (add_tail) với độ phức tạp O(1) tuyệt đối mà không cần cấp phát lại mảng. Thao tác xóa theo ID tốn O(n) tìm kiếm và O(1) ngắt liên kết con trỏ.",

    // Module 2
    m2Title: "Phân Hệ 2: Giỏ Hàng Hoàn Tác (Stack LIFO) & Hàng Đợi Flash Sale (Queue FIFO)",
    m2Desc: "Ngăn xếp (Stack) lưu lịch sử xóa để hoàn tác (LIFO). Hàng đợi (Queue) điều phối các đơn hàng đồng thời trong đợt Flash Sale theo thứ tự đến trước - xử lý trước (FIFO).",
    m2Explain: "Nguyên lý hoạt động: Ngăn xếp (Stack) hoạt động theo cơ chế Last-In First-Out (LIFO), cho phép khôi phục chính xác mặt hàng vừa bị xóa khỏi giỏ. Hàng đợi (Queue) hoạt động theo cơ chế First-In First-Out (FIFO), ngăn chặn hiện tượng tranh chấp đơn hàng (race condition) và bảo đảm tính công bằng khi trừ tồn kho trong sự kiện Flash Sale.",

    // Module 3
    m3Title: "Phân Hệ 3: Chỉ Mục Tra Cứu Tốc Độ Cao (BST & Cây Cân Bằng Tự Động AVL)",
    m3Desc: "Cây nhị phân tìm kiếm (BST) tra cứu theo ID đạt O(log n) trung bình. Cây AVL tự cân bằng với 4 phép quay (LL, RR, LR, RL) triệt tiêu hoàn toàn nguy cơ suy biến thành O(n) khi dữ liệu ID tăng dần.",
    m3Explain: "Nguyên lý hoạt động: Trên cây BST thông thường, nếu khóa ID nạp vào theo thứ tự tăng dần, cây sẽ suy thoái thành danh sách liên kết với chiều cao h = n và tìm kiếm tốn O(n). Cây AVL theo dõi hệ số cân bằng BF = h(trái) - h(phải) và tự động thực hiện phép quay đơn hoặc kép để luôn bảo đảm chiều cao h ≤ 1.44 log₂(n).",

    // Module 4
    m4Title: "Phân Hệ 4: Động Cơ Lọc & Sắp Xếp Dữ Liệu (O(n²) vs O(n log n))",
    m4Desc: "Đối chiếu trực quan giữa nhóm cơ bản O(n²) (Bubble, Selection, Insertion Sort) và nhóm nâng cao O(n log n) (QuickSort Median-of-Three, MergeSort).",
    m4Explain: "Nguyên lý hoạt động: Các thuật toán O(n²) cần xấp xỉ n² phép so sánh, phù hợp cho tập dữ liệu nhỏ (N ≤ 3,000) nhưng mất hàng giờ khi N = 100,000. QuickSort chia để trị với chốt trung vị của ba (Median-of-Three) và MergeSort bảo đảm thời gian chạy O(n log n), hoàn thành sắp xếp 100,000 phần tử chỉ trong chưa đầy 0.3 giây.",

    // Module 5
    m5Title: "Phân Hệ 5: Tìm Kiếm Tức Thì (Bảng Băm) & Lịch Sử Tự Tổ Chức (MTF vs Transpose)",
    m5Desc: "Bảng băm (Hash Table) với hàm băm đa thức cuộn và Separate Chaining đạt O(1) tra cứu tên sản phẩm. Danh sách tự tổ chức tối ưu hóa truy vấn lặp lại theo phân phối Zipf 80/20.",
    m5Explain: "Nguyên lý hoạt động: Bảng băm chuyển đổi chuỗi tên thành chỉ số mảng bằng hàm băm đa thức H(s) = ∑ s[i]·31ⁱ mod M và giải quyết xung đột bằng danh sách liên kết đơn. Khi hệ số tải α > 0.75, bảng tự động rehash nhân đôi kích thước. Danh sách tự tổ chức (Self-organizing List) đưa từ khóa truy cập lên đầu (Move-to-Front) hoặc đổi chỗ với phần tử trước (Transpose) để giảm số lần thăm dò trung bình.",

    // Common
    howItWorks: "Nguyên lý & Phân tích độ phức tạp (Dành cho vấn đáp bảo vệ):",
    measuredTime: "Thời gian đo đạc thực tế lõi Python (perf_counter):",
    theoreticalComplexity: "Độ phức tạp lý thuyết:",
    educationalNotice: "Lưu ý: Mô phỏng từng bước trên tập dữ liệu nhỏ (10-20 phần tử) phục vụ mục đích minh họa sư phạm trực quan.",
    emptyNotice: "Chưa có dữ liệu để hiển thị."
  },
  en: {
    appTitle: "MINI E-COMMERCE CORE ENGINE",
    appSubtitle: "Data Structures & Algorithms Term Project • 100,000+ Products",
    navDashboard: "Dashboard",
    navCatalog: "1. Inventory (DLL)",
    navCart: "2. Cart & Flash Sale (Stack/Queue)",
    navTree: "3. Tree Index (BST/AVL)",
    navSort: "4. Sort & Filter (O(n²) vs O(n log n))",
    navSearch: "5. Search & History (Hash/MTF)",
    navBenchmarks: "Benchmarks (Charts)",
    navMemory: "Memory & Cleanup",

    // System stats
    systemStatus: "System Status",
    loadedProducts: "Loaded Products",
    currentMemory: "Current Memory",
    peakMemory: "Peak Memory",
    structuresBuilt: "Built Structures",

    // Actions
    quickActions: "Quick Actions",
    load100k: "Load 100,000 Products",
    buildIndexes: "Build All Indexes",
    runDemo: "Run Demo Scenarios",
    releaseMemory: "Release Memory (GC)",

    // Module 1
    m1Title: "Module 1: Dynamic Inventory Management (Doubly Linked List)",
    m1Desc: "Dynamic storage via Doubly Linked List without static arrays. O(1) head/tail insertions, bidirectional traversal, server-side pagination, and explicit memory teardown.",
    m1Explain: "How it works: The doubly linked list links nodes with prev and next pointers, enabling O(1) add_head and add_tail without array reallocation. Deletion by ID requires O(n) search and O(1) pointer unlinking.",

    // Module 2
    m2Title: "Module 2: Cart Undo (LIFO Stack) & Flash Sale Queue (FIFO Queue)",
    m2Desc: "Linked Stack records deletion history for LIFO rollback. Linked Queue schedules concurrent Flash Sale orders in FIFO order.",
    m2Explain: "How it works: Stack operates on Last-In First-Out (LIFO) allowing instant restoration of removed items. Queue operates on First-In First-Out (FIFO), preventing race conditions and guaranteeing fair order fulfillment during traffic spikes.",

    // Module 3
    m3Title: "Module 3: High-Speed ID Index (BST & Self-Balancing AVL Tree)",
    m3Desc: "Binary Search Tree (BST) offers O(log n) average lookup. Self-balancing AVL tree enforces balance via 4 rotations (LL, RR, LR, RL), bounding height to h ≤ 1.44 log₂(n).",
    m3Explain: "How it works: Sorted input degenerates a naive BST into an O(n) linked list. AVL tracks balance factor BF = h(left) - h(right) and performs single or double rotations on insertion and deletion to strictly preserve logarithmic depth.",

    // Module 4
    m4Title: "Module 4: Filtering & Sorting Engine (O(n²) vs O(n log n))",
    m4Desc: "Direct comparison between basic O(n²) sorts (Bubble, Selection, Insertion) and advanced O(n log n) recursive sorts (QuickSort Median-of-Three, MergeSort).",
    m4Explain: "How it works: O(n²) sorts require ~n² comparisons, feasible for N ≤ 3,000 but requiring hours at N = 100,000. QuickSort with Median-of-Three and MergeSort guarantee O(n log n), sorting 100,000 items in under 0.3 seconds.",

    // Module 5
    m5Title: "Module 5: Instant Search (Hash Table) & Self-Organizing History (MTF vs Transpose)",
    m5Desc: "Hash Table with polynomial rolling hash and Separate Chaining achieves O(1) average lookup. Self-organizing list optimizes repeated queries under Zipf 80/20 distributions.",
    m5Explain: "How it works: Hash Table maps product names via H(s) = ∑ s[i]·31ⁱ mod M and chains collisions with singly linked lists. Automatically rehashes when load factor α > 0.75. Self-organizing list moves accessed items to head (Move-to-Front) or swaps with predecessor (Transpose).",

    // Common
    howItWorks: "How it works & Complexity Analysis (For Oral Defense):",
    measuredTime: "Core-measured Python latency (perf_counter):",
    theoreticalComplexity: "Theoretical Big-O Complexity:",
    educationalNotice: "Note: Step-by-step small animations (10-20 items) are strictly for educational illustration.",
    emptyNotice: "No records to display."
  }
};
